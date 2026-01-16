#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ಕಪಿಲ ಸಂಕಲನ (Kapila Compiler)
==============================

Compiles Kapila source to C code.

Usage:
    kapilac input.kpl              # Output to stdout
    kapilac input.kpl -o output.c  # Output to file
    kapilac input.kpl -r           # Compile and run
"""

import sys
import os
import argparse
import subprocess
import tempfile
import shutil

# Handle PyInstaller frozen mode
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    kapila_dir = os.path.dirname(sys.executable)
else:
    # Running as script
    kapila_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, kapila_dir)

from src.parser import parse
from src.codegen import generate_c

# Runtime location
RUNTIME_DIR = os.path.join(kapila_dir, 'runtime')
RUNTIME_H = os.path.join(RUNTIME_DIR, 'kapila.h')
RUNTIME_C = os.path.join(RUNTIME_DIR, 'kapila.c')

# Bundled TinyCC location
TCC_DIR = os.path.join(kapila_dir, 'tcc')
TCC_EXE = os.path.join(TCC_DIR, 'tcc.exe')


def find_c_compiler():
    """Find C compiler: bundled TinyCC first, then GCC."""
    # 1. Check for bundled TinyCC (preferred - self-contained)
    if os.path.exists(TCC_EXE):
        return TCC_EXE, 'tcc'

    # 2. Check tools/tcc (development location)
    dev_tcc = os.path.join(kapila_dir, 'tools', 'tcc', 'tcc.exe')
    if os.path.exists(dev_tcc):
        return dev_tcc, 'tcc'

    # 3. Check for TinyCC in PATH
    try:
        result = subprocess.run(['tcc', '-v'], capture_output=True)
        if result.returncode == 0:
            return 'tcc', 'tcc'
    except FileNotFoundError:
        pass

    # 4. Windows: check common GCC locations
    if os.name == 'nt':
        # Check WinGet install location
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

    # 5. Try GCC in PATH
    try:
        result = subprocess.run(['gcc', '--version'], capture_output=True)
        if result.returncode == 0:
            return 'gcc', 'gcc'
    except FileNotFoundError:
        pass

    return None, None


def compile_to_c(source: str) -> str:
    """Compile Kapila source to C code."""
    program = parse(source)
    return generate_c(program)


def setup_console():
    """Set up console for UTF-8 output on Windows."""
    if os.name == 'nt':
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleOutputCP(65001)
        except:
            pass
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass


def main():
    setup_console()

    parser = argparse.ArgumentParser(
        description='ಕಪಿಲ ಸಂಕಲನ (Kapila Compiler) - Compile Kapila to C'
    )
    parser.add_argument('input', nargs='?', help='Input .kpl file (or - for stdin)')
    parser.add_argument('-o', '--output', help='Output C file')
    parser.add_argument('-r', '--run', action='store_true', help='Compile and run')
    parser.add_argument('-c', '--code', help='Compile code directly')
    parser.add_argument('-k', '--keep', action='store_true', help='Keep generated files')
    parser.add_argument('-v', '--version', action='store_true', help='Show version')

    args = parser.parse_args()

    if args.version:
        print("ಕಪಿಲ (Kapila) Compiler v0.6.0")
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

    # Compile to C
    c_code = compile_to_c(source)

    # Output
    if args.run:
        # Find C compiler
        cc, cc_type = find_c_compiler()
        if not cc:
            print("Error: No C compiler found!", file=sys.stderr)
            print("Please install GCC/MinGW or ensure TinyCC is bundled.", file=sys.stderr)
            return

        # Create temp directory for compilation
        temp_dir = tempfile.mkdtemp(prefix='kapila_')
        c_file = os.path.join(temp_dir, 'program.c')
        runtime_h = os.path.join(temp_dir, 'kapila.h')
        runtime_c = os.path.join(temp_dir, 'kapila.c')
        exe_file = os.path.join(temp_dir, 'program.exe' if os.name == 'nt' else 'program')

        try:
            # Copy runtime files
            shutil.copy(RUNTIME_H, runtime_h)
            shutil.copy(RUNTIME_C, runtime_c)

            # Write generated code
            with open(c_file, 'w', encoding='utf-8') as f:
                f.write(c_code)

            # Build compiler command
            if cc_type == 'tcc':
                # TinyCC: need to specify include path for its headers
                tcc_dir = os.path.dirname(cc)
                tcc_include = os.path.join(tcc_dir, 'include')
                tcc_lib = os.path.join(tcc_dir, 'lib')
                compile_cmd = [cc, '-o', exe_file, c_file, runtime_c,
                               '-I', tcc_include, '-L', tcc_lib]
            else:
                # GCC
                compile_cmd = [cc, '-o', exe_file, c_file, runtime_c, '-O2']

            # Compile
            result = subprocess.run(
                compile_cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                cwd=temp_dir
            )
            if result.returncode != 0:
                print("Compilation error:", result.stderr, file=sys.stderr)
                if args.keep:
                    print(f"Files kept in: {temp_dir}")
                return

            # Run
            result = subprocess.run([exe_file], capture_output=True, text=True,
                                    encoding='utf-8', errors='replace')
            print(result.stdout, end='')
            if result.stderr:
                print(result.stderr, end='', file=sys.stderr)

            if args.keep:
                print(f"\nFiles kept in: {temp_dir}")

        finally:
            # Cleanup unless -k flag
            if not args.keep and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

    elif args.output:
        # When outputting to file, copy runtime alongside
        output_dir = os.path.dirname(os.path.abspath(args.output))
        if not output_dir:
            output_dir = '.'
        out_runtime_h = os.path.join(output_dir, 'kapila.h')
        out_runtime_c = os.path.join(output_dir, 'kapila.c')

        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(c_code)

        # Copy runtime if not already there
        if not os.path.exists(out_runtime_h):
            shutil.copy(RUNTIME_H, out_runtime_h)
        if not os.path.exists(out_runtime_c):
            shutil.copy(RUNTIME_C, out_runtime_c)

        print(f"Generated: {args.output}")
        print(f"Runtime: {out_runtime_h}, {out_runtime_c}")
        print(f"\nTo compile: tcc -o program {os.path.basename(args.output)} kapila.c")
        print(f"        or: gcc -o program {os.path.basename(args.output)} kapila.c")
    else:
        print(c_code)


if __name__ == '__main__':
    main()
