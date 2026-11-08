#!/usr/bin/env python3
"""
Build Kapila distribution package with PyInstaller.

Creates:
  dist/kapila/
    kapila.exe     - REPL/Interpreter
    kapilac.exe    - Compiler
    kapila-gui.exe - Desktop window (REPL with live news/weather/wiki)
    runtime/       - C runtime library
    tcc/           - TinyCC compiler
    examples/      - Example programs
"""

import os
import sys
import shutil
import subprocess

# Directories
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(ROOT_DIR, 'dist', 'kapila')
BUILD_DIR = os.path.join(ROOT_DIR, 'build')


def clean():
    """Clean previous builds."""
    print("Cleaning previous builds...")
    for d in [DIST_DIR, BUILD_DIR]:
        if os.path.exists(d):
            shutil.rmtree(d)


def build_interpreter():
    """Build kapila.exe (interpreter/REPL)."""
    print("\nBuilding kapila.exe (interpreter)...")
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',
        '--name', 'kapila',
        '--distpath', DIST_DIR,
        '--workpath', BUILD_DIR,
        '--specpath', BUILD_DIR,
        '--clean',
        'kapila.py'
    ]
    subprocess.run(cmd, cwd=ROOT_DIR, check=True)


def build_compiler():
    """Build kapilac.exe (compiler)."""
    print("\nBuilding kapilac.exe (compiler)...")
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',
        '--name', 'kapilac',
        '--distpath', DIST_DIR,
        '--workpath', BUILD_DIR,
        '--specpath', BUILD_DIR,
        '--clean',
        'kapilac.py'
    ]
    subprocess.run(cmd, cwd=ROOT_DIR, check=True)


def build_gui():
    """Build kapila-gui.exe (windowed REPL, no console)."""
    print("\nBuilding kapila-gui.exe (desktop GUI)...")
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',
        '--windowed',
        '--name', 'kapila-gui',
        '--icon', os.path.join(ROOT_DIR, 'static', 'kapila.ico'),
        '--add-data', os.path.join(ROOT_DIR, 'static', 'kapila.ico') + os.pathsep + 'static',
        '--distpath', DIST_DIR,
        '--workpath', BUILD_DIR,
        '--specpath', BUILD_DIR,
        '--clean',
        'kapila_gui.py'
    ]
    subprocess.run(cmd, cwd=ROOT_DIR, check=True)


def publish_gui():
    """Copy the GUI to static/downloads so the website serves it."""
    dst_dir = os.path.join(ROOT_DIR, 'static', 'downloads')
    os.makedirs(dst_dir, exist_ok=True)
    dst = os.path.join(dst_dir, 'kapila-gui-windows-x64.exe')
    shutil.copy(os.path.join(DIST_DIR, 'kapila-gui.exe'), dst)
    print(f"Copied for download: {dst}")


def copy_runtime():
    """Copy runtime files."""
    print("\nCopying runtime files...")
    runtime_src = os.path.join(ROOT_DIR, 'runtime')
    runtime_dst = os.path.join(DIST_DIR, 'runtime')
    if os.path.exists(runtime_dst):
        shutil.rmtree(runtime_dst)
    shutil.copytree(runtime_src, runtime_dst)


def copy_tcc():
    """Copy TinyCC compiler."""
    print("\nCopying TinyCC...")
    tcc_src = os.path.join(ROOT_DIR, 'tools', 'tcc')
    tcc_dst = os.path.join(DIST_DIR, 'tcc')
    if os.path.exists(tcc_dst):
        shutil.rmtree(tcc_dst)
    shutil.copytree(tcc_src, tcc_dst)


def copy_examples():
    """Copy example files."""
    print("\nCopying examples...")
    examples_dst = os.path.join(DIST_DIR, 'examples')
    os.makedirs(examples_dst, exist_ok=True)

    examples_src = os.path.join(ROOT_DIR, 'examples')
    for f in os.listdir(examples_src):
        if f.endswith('.kpl'):
            shutil.copy(
                os.path.join(examples_src, f),
                os.path.join(examples_dst, f)
            )


def create_readme():
    """Create README for distribution."""
    print("\nCreating README...")
    readme = """# ಕಪಿಲ (Kapila) - Kannada Programming Language

A native Kannada programming language that compiles to machine code.

## Quick Start

1. Open Command Prompt in this folder
2. Run the REPL:
   ```
   kapila.exe
   ```
3. Or compile and run a program:
   ```
   kapilac.exe examples\\hello.kpl -r
   ```

## Commands

- `kapila.exe` - Interactive REPL (interpreter)
- `kapilac.exe file.kpl -r` - Compile and run
- `kapilac.exe file.kpl -o out.c` - Generate C code
- `kapilac.exe -v` - Show version and compiler info

## Example Program (examples/hello.kpl)

```
// Define square word
ವರ್ಗ: ನಕಲು ಗುಣಿಸು ॥

// Arithmetic
೫ ೩ ಕೂಡು ಮುದ್ರಿಸು.    // 8
೫ ವರ್ಗ ಮುದ್ರಿಸು.       // 25

// String
"ನಮಸ್ಕಾರ!" ಮುದ್ರಿಸು.
```

## Included Components

- `kapila.exe` - Interpreter/REPL
- `kapilac.exe` - Compiler
- `kapila-gui.exe` - Desktop window: type a line, press Enter
- `runtime/` - C runtime library
- `tcc/` - TinyCC compiler (bundled)
- `examples/` - Sample programs

## Author

Architect and Author: Prashanth Hebbar (hebbarp@gmail.com)
Co-Authored-By: Claude Opus 4.5

## Links

- GitHub: https://github.com/hebbarp/kapila
"""
    with open(os.path.join(DIST_DIR, 'README.md'), 'w', encoding='utf-8') as f:
        f.write(readme)


def create_zip():
    """Create distribution ZIP file."""
    print("\nCreating ZIP archive...")
    zip_name = os.path.join(ROOT_DIR, 'dist', 'kapila-windows-x64')
    shutil.make_archive(zip_name, 'zip', os.path.join(ROOT_DIR, 'dist'), 'kapila')
    print(f"Created: {zip_name}.zip")


def main():
    if '--gui-only' in sys.argv:
        os.makedirs(DIST_DIR, exist_ok=True)
        build_gui()
        publish_gui()
        return

    print("=" * 50)
    print("Building Kapila Distribution")
    print("=" * 50)

    clean()
    build_interpreter()
    build_compiler()
    build_gui()
    copy_runtime()
    copy_tcc()
    copy_examples()
    create_readme()
    create_zip()
    publish_gui()

    print("\n" + "=" * 50)
    print("Build complete!")
    print(f"Distribution: {DIST_DIR}")
    print(f"ZIP file: dist/kapila-windows-x64.zip")
    print("=" * 50)


if __name__ == '__main__':
    main()
