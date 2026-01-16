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

kapila_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, kapila_dir)

from src.parser import parse
from src.codegen import generate_c


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
        # Write to temp file, compile with gcc, run
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False, encoding='utf-8') as f:
            f.write(c_code)
            c_file = f.name

        exe_file = c_file.replace('.c', '.exe' if os.name == 'nt' else '')

        try:
            # Compile
            result = subprocess.run(
                ['gcc', '-o', exe_file, c_file, '-O2'],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                print("Compilation error:", result.stderr, file=sys.stderr)
                return

            # Run
            result = subprocess.run([exe_file], capture_output=True, text=True)
            print(result.stdout, end='')
            if result.stderr:
                print(result.stderr, end='', file=sys.stderr)

        finally:
            # Cleanup
            if os.path.exists(c_file):
                os.remove(c_file)
            if os.path.exists(exe_file):
                os.remove(exe_file)

    elif args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(c_code)
        print(f"Generated: {args.output}")
    else:
        print(c_code)


if __name__ == '__main__':
    main()
