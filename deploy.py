#!/usr/bin/env python3
"""Deploy Kapila Web Playground to https://kapila.matsyaai.com (nginx -> gunicorn)"""

import os
import sys
import time
import subprocess

import paramiko

HOST = "139.59.85.251"
USERNAME = "esumadmin"
SSH_KEY = os.path.expanduser("~/.ssh/id_ed25519")
DOMAIN = "kapila.matsyaai.com"
NGINX_SITE = f"/etc/nginx/sites-available/{DOMAIN}"
REMOTE_PATH = "/var/www/kapilaweb"
TEMP_PATH = "/tmp/kapila_deploy"

LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))

# Files to deploy (relative to LOCAL_DIR)
FILES = [
    "app.py",
    "templates/index.html",
    "templates/landing.html",
    "templates/wiki.html",
    "static/og.png",
    "static/kasuti.svg",
    "static/downloads/kapila-gui-windows-x64.exe",
    "lib/prelude.kpl",
    # src package
    "src/__init__.py",
    "src/vocabulary.py",
    "src/repl.py",
    # lexer
    "src/lexer/__init__.py",
    "src/lexer/lexer.py",
    "src/lexer/tokens.py",
    "src/lexer/keywords.py",
    # parser
    "src/parser/__init__.py",
    "src/parser/parser.py",
    "src/parser/ast.py",
    # vm
    "src/vm/__init__.py",
    "src/vm/vm.py",
    "src/vm/builtins.py",
    "src/vm/records.py",
    "src/vm/sources.py",
    "src/vm/trace.py",
    # unicode
    "src/unicode/__init__.py",
    "src/unicode/kannada.py",
    "src/unicode/hindi.py",
    "src/unicode/telugu.py",
    # sandarbha (context resolver)
    "src/sandarbha/__init__.py",
    "src/sandarbha/context.py",
    "src/sandarbha/frames.py",
    "src/sandarbha/vibhakti.py",
    # semantic
    "src/semantic/__init__.py",
    "src/semantic/types.py",
    "src/semantic/checker.py",
    # codegen
    "src/codegen/__init__.py",
    "src/codegen/c_generator.py",
    # examples
    "examples/hello.kpl",
    "examples/basics.kpl",
    "examples/list_test.kpl",
    "examples/runtime_test.kpl",
    "examples/mashables.kpl",
    # NL engine
    "nl_engine.py",
    "nl_weights.json",
]

# External dependencies to copy into the deploy
# (source_dir, files_relative_to_source)
EXTERNAL_DEPS = [
    # PicoNN from D:/atrimed/sales
    ("D:/atrimed/sales", [
        "piconn/__init__.py",
        "piconn/engine.py",
        "piconn/nn.py",
        "piconn/optim.py",
        "piconn/loss.py",
        "piconn/functional.py",
        "piconn/data.py",
    ]),
    # Pampa core from D:/pampa
    ("D:/pampa", [
        "core/__init__.py",
        "core/scripts.py",
        "core/akshara.py",
        "core/maatra.py",
    ]),
]


# Every wiki page, including the generated Build-Status.md
FILES += sorted(f"wiki/{n}" for n in os.listdir(os.path.join(LOCAL_DIR, "wiki")) if n.endswith(".md"))


def safe_print(msg):
    """Print with ASCII fallback for Windows console."""
    try:
        print(msg, flush=True)
    except UnicodeEncodeError:
        print(msg.encode("ascii", errors="replace").decode(), flush=True)


def connect():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USERNAME, key_filename=SSH_KEY, timeout=30)
    safe_print(f"Connected to {HOST}")
    return ssh


def run(ssh, cmd, sudo=False):
    if sudo:
        cmd = f"sudo -n bash -c '{cmd}'"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode("utf-8", errors="replace").strip()
    err = stderr.read().decode("utf-8", errors="replace").strip()
    if out:
        safe_print(f"  {out}")
    # Filter out sudo password prompt noise
    if err and "[sudo]" not in err:
        safe_print(f"  ERR: {err}")
    return out


def deploy():
    safe_print("Regenerating the build status page...")
    subprocess.run([sys.executable, os.path.join("tools", "build_status.py")], cwd=LOCAL_DIR)

    ssh = connect()
    sftp = ssh.open_sftp()

    # 1. Create temp dir
    safe_print("\n[1/6] Preparing temp directory...")
    run(ssh, f"rm -rf {TEMP_PATH} && mkdir -p {TEMP_PATH}")

    # 2. Upload files
    safe_print("\n[2/6] Uploading files...")
    for f in FILES:
        local = os.path.join(LOCAL_DIR, f)
        if not os.path.exists(local):
            safe_print(f"  SKIP (not found): {f}")
            continue

        remote_dir = os.path.dirname(f"{TEMP_PATH}/{f}")
        run(ssh, f"mkdir -p {remote_dir}")
        sftp.put(local, f"{TEMP_PATH}/{f}")
        safe_print(f"  {f}")

    # 2b. Upload external dependencies
    safe_print("\n  External dependencies...")
    for src_dir, dep_files in EXTERNAL_DEPS:
        for f in dep_files:
            local = os.path.join(src_dir, f)
            if not os.path.exists(local):
                safe_print(f"  SKIP (not found): {src_dir}/{f}")
                continue
            remote_dir = os.path.dirname(f"{TEMP_PATH}/{f}")
            run(ssh, f"mkdir -p {remote_dir}")
            sftp.put(local, f"{TEMP_PATH}/{f}")
            safe_print(f"  {f}")

    # 3. Upload wsgi + service files
    safe_print("\n[3/6] Creating server configs...")

    # wsgi.py
    wsgi_content = """import sys, os
sys.path.insert(0, '/var/www/kapilaweb')
os.chdir('/var/www/kapilaweb')
from app import app as application

# Pre-train NL engine during preload (before worker fork)
try:
    from nl_engine import get_engine, KapilaNLEngine
    # Use fewer epochs on server for faster startup
    KapilaNLEngine._server_epochs = 20
    _orig_train = KapilaNLEngine.train
    def _fast_train(self, epochs=80, lr=0.05):
        return _orig_train(self, epochs=getattr(self.__class__, '_server_epochs', epochs), lr=lr)
    KapilaNLEngine.train = _fast_train
    print("Training NL engine (20 epochs)...")
    get_engine()
    print("NL engine ready.")
except Exception as e:
    print(f"NL engine training failed: {e}")
"""
    with sftp.open(f"{TEMP_PATH}/wsgi.py", "w") as f:
        f.write(wsgi_content)
    safe_print("  wsgi.py")

    # systemd service
    service_content = """[Unit]
Description=Kapila Web Playground
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/kapilaweb
ExecStart=/usr/bin/python3 -m gunicorn --bind 127.0.0.1:5050 --workers 2 --timeout 120 --preload wsgi:application
Restart=always
RestartSec=5
# Playground runs untrusted code; timed-out runs keep spinning in their
# thread, so cap what the service can take from the shared box.
CPUQuota=50%
MemoryMax=512M
StandardOutput=append:/var/log/kapila.log
StandardError=append:/var/log/kapila.log

[Install]
WantedBy=multi-user.target
"""
    with sftp.open(f"{TEMP_PATH}/kapila.service", "w") as f:
        f.write(service_content)
    safe_print("  kapila.service")

    sftp.close()

    # 4. Move to final location
    safe_print("\n[4/6] Installing to /var/www/kapilaweb...")
    run(ssh, f"mkdir -p {REMOTE_PATH}", sudo=True)
    run(ssh, f"cp -r {TEMP_PATH}/* {REMOTE_PATH}/", sudo=True)
    run(ssh, f"chown -R www-data:www-data {REMOTE_PATH}", sudo=True)

    # 5. Install dependencies + setup service + Apache config
    safe_print("\n[5/6] Installing dependencies & configuring...")

    # Install flask + gunicorn via apt
    run(ssh, "apt install -y python3-flask python3-markdown gunicorn 2>/dev/null", sudo=True)

    # Install systemd service
    run(ssh, f"cp {REMOTE_PATH}/kapila.service /etc/systemd/system/kapila.service", sudo=True)
    run(ssh, "systemctl daemon-reload", sudo=True)
    run(ssh, "systemctl enable kapila", sudo=True)
    run(ssh, "systemctl restart kapila", sudo=True)

    # nginx front proxy for the subdomain. Only installed the first time:
    # certbot then rewrites the site file with the TLS server block.
    exists = run(ssh, f"test -e {NGINX_SITE} && echo yes || echo no")
    if exists == "no":
        safe_print(f"  Installing nginx site for {DOMAIN}...")
        sftp2 = ssh.open_sftp()
        sftp2.put(os.path.join(LOCAL_DIR, "deploy", "kapila.nginx.conf"), f"{TEMP_PATH}/kapila.nginx.conf")
        sftp2.close()
        run(ssh, f"cp {TEMP_PATH}/kapila.nginx.conf {NGINX_SITE}", sudo=True)
        run(ssh, f"ln -sf {NGINX_SITE} /etc/nginx/sites-enabled/{DOMAIN}", sudo=True)
        run(ssh, "nginx -t 2>&1 && systemctl reload nginx", sudo=True)
        run(ssh, f"certbot --nginx -d {DOMAIN} --non-interactive --redirect 2>&1 | tail -3", sudo=True)
    else:
        safe_print(f"  nginx site for {DOMAIN} already installed")

    # 6. Verify
    safe_print("\n[6/6] Verifying...")

    # Test import
    run(ssh, "cd /var/www/kapilaweb && python3 -c 'import app' 2>&1")

    time.sleep(3)

    run(ssh, "systemctl status kapila --no-pager 2>&1 | head -10", sudo=True)
    run(ssh, "curl -s -o /dev/null -w 'HTTP %{http_code}' http://127.0.0.1:5050/ 2>/dev/null || echo 'waiting...'")

    # Cleanup
    run(ssh, f"rm -rf {TEMP_PATH}")

    safe_print(f"\nDone! Check: https://{DOMAIN}")
    ssh.close()


if __name__ == "__main__":
    deploy()
