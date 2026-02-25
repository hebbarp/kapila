#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ಕಪಿಲ ಸಂಕಲನ (Kapila Compiler)
==============================

Compiles Kapila source to native executable via C code generation.

Usage:
    kapilac input.kpl              # Compile to executable
    kapilac input.kpl -r           # Compile and run
    kapilac input.kpl --emit-c     # Output generated C code
    kapilac input.kpl -o output    # Specify output name
    kapilac input.kpl --emit-llvm  # Output LLVM IR (requires llvmlite)
"""

import sys
import os
import argparse
import subprocess
import tempfile
import shutil

# Handle PyInstaller frozen mode
if getattr(sys, 'frozen', False):
    kapila_dir = os.path.dirname(sys.executable)
else:
    kapila_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, kapila_dir)

from src.parser import parse
from src.codegen.c_generator import generate_c

# Runtime location
RUNTIME_DIR = os.path.join(kapila_dir, 'runtime')
RUNTIME_H = os.path.join(RUNTIME_DIR, 'kapila.h')
RUNTIME_C = os.path.join(RUNTIME_DIR, 'kapila.c')

# Bundled TinyCC location
TCC_DIR = os.path.join(kapila_dir, 'tcc')
TCC_EXE = os.path.join(TCC_DIR, 'tcc.exe')


def find_c_compiler():
    """Find C compiler: gcc, clang, or tcc."""
    # 1. Check for GCC
    if os.name == 'nt':
        # Windows: check common GCC locations
        winget_path = os.path.expandvars(r'%LOCALAPPDATA%\Microsoft\WinGet\Packages')
        if os.path.exists(winget_path):
            for item in os.listdir(winget_path):
                if 'mingw' in item.lower() or 'winlibs' in item.lower():
                    gcc_path = os.path.join(winget_path, item, 'mingw64', 'bin', 'gcc.exe')
                    if os.path.exists(gcc_path):
                        return gcc_path, 'gcc'

        common_paths = [
            r'C:\Program Files\mingw64\bin\gcc.exe',
            r'C:\mingw64\bin\gcc.exe',
            r'C:\msys64\mingw64\bin\gcc.exe',
        ]
        for path in common_paths:
            if os.path.exists(path):
                return path, 'gcc'

    try:
        result = subprocess.run(['gcc', '--version'], capture_output=True)
        if result.returncode == 0:
            return 'gcc', 'gcc'
    except FileNotFoundError:
        pass

    # 2. Check for clang
    try:
        result = subprocess.run(['clang', '--version'], capture_output=True)
        if result.returncode == 0:
            return 'clang', 'clang'
    except FileNotFoundError:
        pass

    # 3. Check for bundled TinyCC
    if os.path.exists(TCC_EXE):
        return TCC_EXE, 'tcc'

    # 4. Check for TinyCC in PATH
    try:
        result = subprocess.run(['tcc', '-v'], capture_output=True)
        if result.returncode == 0:
            return 'tcc', 'tcc'
    except FileNotFoundError:
        pass

    return None, None


def compile_c_to_executable(c_file, runtime_c, output_exe, cc, cc_type):
    """Compile generated C code + runtime to executable."""
    try:
        if cc_type == 'tcc':
            tcc_dir = os.path.dirname(cc)
            tcc_include = os.path.join(tcc_dir, 'include')
            tcc_lib = os.path.join(tcc_dir, 'lib')
            cmd = [cc, '-o', output_exe, c_file, runtime_c,
                   '-I', tcc_include, '-L', tcc_lib, '-lm']
        else:
            # gcc or clang
            cmd = [cc, '-o', output_exe, c_file, runtime_c, '-O2', '-lm']

        result = subprocess.run(cmd, capture_output=True, text=True,
                                encoding='utf-8', errors='replace')
        if result.returncode != 0:
            print(f"Compilation error: {result.stderr}", file=sys.stderr)
            return False
        return True
    except Exception as e:
        print(f"Compilation error: {e}", file=sys.stderr)
        return False


def setup_console():
    """Set up console for UTF-8 output on Windows."""
    if os.name == 'nt':
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleOutputCP(65001)
        except Exception:
            pass
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass


def main():
    setup_console()

    parser = argparse.ArgumentParser(
        description='ಕಪಿಲ ಸಂಕಲನ (Kapila Compiler) - Compile Kapila to native code'
    )
    parser.add_argument('input', nargs='?', help='Input .kpl file (or - for stdin)')
    parser.add_argument('-o', '--output', help='Output file (executable or .c)')
    parser.add_argument('-r', '--run', action='store_true', help='Compile and run')
    parser.add_argument('-c', '--code', help='Compile code directly')
    parser.add_argument('-k', '--keep', action='store_true', help='Keep generated files')
    parser.add_argument('-v', '--version', action='store_true', help='Show version')
    parser.add_argument('--emit-c', action='store_true', help='Output generated C code')
    parser.add_argument('--emit-llvm', action='store_true', help='Output LLVM IR (requires llvmlite)')

    args = parser.parse_args()

    if args.version:
        print("ಕಪಿಲ (Kapila) Compiler v0.8.0 (C backend)")
        cc, cc_type = find_c_compiler()
        if cc:
            print(f"C Compiler: {cc_type} ({cc})")
        else:
            print("C Compiler: not found")
        return

    # Get source
    if args.code:
        source = args.code
    elif args.input == '-' or (not args.input and not sys.stdin.isatty()):
        source = sys.stdin.read()
    elif args.input:
        with open(args.input, 'r', encoding='utf-8') as f:
            source = f.read()
    else:
        parser.print_help()
        return

    # LLVM mode (optional, requires llvmlite)
    if args.emit_llvm:
        try:
            from src.codegen import generate_llvm
            program = parse(source)
            llvm_ir = generate_llvm(program)
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(llvm_ir)
                print(f"Generated: {args.output}")
            else:
                print(llvm_ir)
        except ImportError:
            print("Error: llvmlite is required for --emit-llvm.", file=sys.stderr)
            print("Install it with: pip install llvmlite", file=sys.stderr)
            sys.exit(1)
        return

    # Prepend standard library prelude
    prelude_path = os.path.join(kapila_dir, 'lib', 'prelude.kpl')
    if os.path.exists(prelude_path):
        with open(prelude_path, 'r', encoding='utf-8') as f:
            source = f.read() + '\n' + source

    # Parse and generate C code
    program = parse(source)
    c_code = generate_c(program)

    # Emit C mode
    if args.emit_c:
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(c_code)
            print(f"Generated: {args.output}")
        else:
            print(c_code)
        return

    # Default: compile to executable
    cc, cc_type = find_c_compiler()
    if not cc:
        print("Error: No C compiler found!", file=sys.stderr)
        print("Please install GCC, Clang, or MinGW.", file=sys.stderr)
        sys.exit(1)

    # Create temp directory
    temp_dir = tempfile.mkdtemp(prefix='kapila_')
    c_file = os.path.join(temp_dir, 'program.c')
    runtime_c = os.path.join(temp_dir, 'kapila.c')
    runtime_h = os.path.join(temp_dir, 'kapila.h')

    if args.output:
        exe_file = args.output
    else:
        base = os.path.splitext(os.path.basename(args.input or 'program'))[0]
        exe_file = os.path.join(temp_dir, base + ('.exe' if os.name == 'nt' else ''))

    try:
        # Write generated C code
        with open(c_file, 'w', encoding='utf-8') as f:
            f.write(c_code)

        # Copy runtime files
        shutil.copy(RUNTIME_H, runtime_h)
        shutil.copy(RUNTIME_C, runtime_c)

        # Compile
        if not compile_c_to_executable(c_file, runtime_c, exe_file, cc, cc_type):
            sys.exit(1)

        if args.run:
            result = subprocess.run([exe_file], capture_output=True, text=True,
                                    encoding='utf-8', errors='replace')
            print(result.stdout, end='')
            if result.stderr:
                print(result.stderr, end='', file=sys.stderr)
            sys.exit(result.returncode)
        else:
            print(f"Generated: {exe_file}")

        if args.keep:
            print(f"Files kept in: {temp_dir}")

    finally:
        # Cleanup unless -k flag or output is in temp_dir
        if not args.keep:
            if args.output:
                # Output is outside temp dir, safe to clean up
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
            elif args.run:
                # Was just a run, clean up
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)


if __name__ == '__main__':
    main()
