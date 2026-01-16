#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ಕಪಿಲ ಸಂಕಲನ (Kapila Compiler)
==============================

Compiles Kapila source to C code.

Usage:
    python kapilac.py input.kpl              # Output to stdout
    python kapilac.py input.kpl -o output.c  # Output to file
    python kapilac.py input.kpl -r           # Compile and run
"""

import sys
import os
import argparse
import subprocess
import tempfile
import shutil

kapila_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, kapila_dir)

from src.parser import parse
from src.codegen import generate_c

# Runtime location
RUNTIME_DIR = os.path.join(kapila_dir, 'runtime')
RUNTIME_H = os.path.join(RUNTIME_DIR, 'kapila.h')
RUNTIME_C = os.path.join(RUNTIME_DIR, 'kapila.c')


def find_gcc():
    """Find gcc, checking common locations on Windows."""
    # Windows: check common locations first
    if os.name == 'nt':
        common_paths = [
            r'C:\Users\Admin\AppData\Local\Microsoft\WinGet\Packages\BrechtSanders.WinLibs.POSIX.UCRT_Microsoft.Winget.Source_8wekyb3d8bbwe\mingw64\bin\gcc.exe',
            r'C:\Program Files\mingw64\bin\gcc.exe',
            r'C:\mingw64\bin\gcc.exe',
            r'C:\msys64\mingw64\bin\gcc.exe',
        ]
        # Check WinGet install location
        winget_path = os.path.expandvars(
            r'%LOCALAPPDATA%\Microsoft\WinGet\Packages'
        )
        if os.path.exists(winget_path):
            for item in os.listdir(winget_path):
                if 'mingw' in item.lower() or 'winlibs' in item.lower():
                    gcc_path = os.path.join(winget_path, item, 'mingw64', 'bin', 'gcc.exe')
                    if os.path.exists(gcc_path):
                        common_paths.insert(0, gcc_path)

        for path in common_paths:
            if os.path.exists(path):
                return path

    # Try PATH
    try:
        result = subprocess.run(['gcc', '--version'], capture_output=True)
        if result.returncode == 0:
            return 'gcc'
    except FileNotFoundError:
        pass

    return 'gcc'  # Hope it's in PATH


def compile_to_c(source: str) -> str:
    """Compile Kapila source to C code."""
    program = parse(source)
    return generate_c(program)


def main():
    parser = argparse.ArgumentParser(
        description='ಕಪಿಲ ಸಂಕಲನ (Kapila Compiler) - Compile Kapila to C'
    )
    parser.add_argument('input', nargs='?', help='Input .kpl file (or - for stdin)')
    parser.add_argument('-o', '--output', help='Output C file')
    parser.add_argument('-r', '--run', action='store_true', help='Compile and run')
    parser.add_argument('-c', '--code', help='Compile code directly')
    parser.add_argument('-k', '--keep', action='store_true', help='Keep generated files')

    args = parser.parse_args()

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

    # Compile
    c_code = compile_to_c(source)

    # Output
    if args.run:
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

            # Find gcc
            gcc = find_gcc()

            # Compile with runtime
            result = subprocess.run(
                [gcc, '-o', exe_file, c_file, runtime_c, '-O2'],
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
            result = subprocess.run([exe_file], capture_output=True, text=True, encoding='utf-8', errors='replace')
            # Set Windows console to UTF-8 for proper Kannada output
            if os.name == 'nt':
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleOutputCP(65001)  # UTF-8
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
            print(result.stdout, end='')
            if result.stderr:
                sys.stderr.reconfigure(encoding='utf-8', errors='replace')
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
        print(f"\nTo compile: gcc -o program {args.output} kapila.c")
    else:
        print(c_code)


if __name__ == '__main__':
    main()
