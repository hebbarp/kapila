#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ಕಪಿಲ (Kapila) - Entry Point
============================

Run the Kapila REPL or execute a file.

Usage:
    python kapila.py              # Start REPL
    python kapila.py file.kpl     # Run file
"""

import sys
import os
import io

# Fix Windows console encoding for Kannada
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Setup path
kapila_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, kapila_dir)

from src.vm import VM, KapilaError
from src.lexer import tokenize


def repl():
    """Run the Kapila REPL."""
    print("ಕಪಿಲ (Kapila) v0.1")
    print("A Kannada programming language")
    print("Type 'exit' to quit, 'help' for help")
    print()

    vm = VM()

    while True:
        try:
            line = input("ಕಪಿಲ> ")
        except EOFError:
            print("\nವಿದಾಯ!")
            break
        except KeyboardInterrupt:
            print("\n^C")
            continue

        line = line.strip()
        if not line:
            continue

        if line in ('exit', 'quit', 'ನಿರ್ಗಮಿಸು'):
            print("ವಿದಾಯ!")
            break

        if line in ('help', 'ಸಹಾಯ'):
            print_help()
            continue

        if line in ('.s', 'stack'):
            print(f"Stack: {vm.stack}")
            continue

        if line in ('.w', 'words'):
            print("Words:", list(vm.words.keys()))
            continue

        if line in ('.v', 'vars'):
            print("Vars:", dict(vm.variables))
            continue

        if line == 'clear':
            vm.stack.clear()
            print("Stack cleared")
            continue

        try:
            result = vm.run(line)
            if vm.stack:
                top = vm.stack[-1]
                if top is not None:
                    print(f"→ {top}")
        except KapilaError as e:
            print(f"ದೋಷ: {e}")
        except Exception as e:
            print(f"Error: {type(e).__name__}: {e}")


def print_help():
    print("""
ಕಪಿಲ ಸಹಾಯ (Kapila Help)
========================

Math (infix):    ೫ + ೧೦       x * ೨       ೧೦ / ೨
Compare:         x > ೫        a = b       ೧೦ ≤ ೨೦
Assign:          x := ೧೦.
Define:          ವರ್ಗ: ನಕಲು * ॥
Conditional:     x > ೫ ? [ "yes" ] [ "no" ]
Print:           "ನಮಸ್ಕಾರ" ಮುದ್ರಿಸು.
List:            [ ೧ ೨ ೩ ]
Map:             ಸಂಖ್ಯೆಗಳು 'ವರ್ಗ ನಕ್ಷೆ.

Stack: ನಕಲು (dup)  ಬಿಡು (drop)  ಅದಲುಬದಲು (swap)
Logic: ಮತ್ತು (and)  ಅಥವಾ (or)  ಅಲ್ಲ (not)

Commands: .s (stack)  .w (words)  .v (vars)  clear  exit
""")


def run_file(filename: str):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            source = f.read()
    except FileNotFoundError:
        print(f"File not found: {filename}")
        sys.exit(1)

    vm = VM()
    try:
        vm.run(source)
    except KapilaError as e:
        print(f"ದೋಷ: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_file(sys.argv[1])
    else:
        repl()
