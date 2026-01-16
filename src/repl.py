# -*- coding: utf-8 -*-
"""
Kapila REPL
===========

Interactive Read-Eval-Print Loop for Kapila.
"""

import sys
from .vm import VM, KapilaError
from .lexer import tokenize


def repl():
    """Run the Kapila REPL."""
    print("ಕಪಿಲ (Kapila) v0.1")
    print("A Kannada programming language")
    print("Type 'ನಿರ್ಗಮಿಸು' or 'exit' to quit, 'ಸಹಾಯ' or 'help' for help")
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

        # Commands
        if line in ('ನಿರ್ಗಮಿಸು', 'exit', 'quit'):
            print("ವಿದಾಯ!")
            break

        if line in ('ಸಹಾಯ', 'help'):
            print_help()
            continue

        if line in ('.s', '.ಸ್ಟಾಕ್', 'stack'):
            print(f"Stack: {vm.stack}")
            continue

        if line in ('.w', '.ಪದಗಳು', 'words'):
            print("Defined words:", list(vm.words.keys()))
            continue

        if line in ('.v', '.ಚರಗಳು', 'vars'):
            print("Variables:", dict(vm.variables))
            continue

        if line == 'clear':
            vm.stack.clear()
            print("Stack cleared")
            continue

        # Execute
        try:
            result = vm.run(line)
            if vm.stack:
                # Show top of stack if not empty
                print(f"→ {vm.stack[-1]}")
        except KapilaError as e:
            print(f"ದೋಷ: {e}")
        except Exception as e:
            print(f"Error: {e}")


def print_help():
    """Print help message."""
    print("""
ಕಪಿಲ ಸಹಾಯ (Kapila Help)
========================

Syntax:
  x + ೫                    Infix math
  "ನಮಸ್ಕಾರ" ಮುದ್ರಿಸು.        Postfix actions
  x := ೧೦.                 Assignment
  ವರ್ಗ: ನಕಲು * ॥           Word definition
  [ ೧ + ] 'ನಕ್ಷೆ           Blocks and quotations
  x > ೫ ? [ "yes" ] [ "no" ]  Conditional

Stack words (ಸ್ಟಾಕ್):
  ನಕಲು (dup)      Duplicate top
  ಬಿಡು (drop)     Discard top
  ಅದಲುಬದಲು (swap) Swap top two

Math: +  -  *  /  %
Compare: =  <  >  ≤  ≥  ≠ (or <=  >=  !=)
Logic: ಮತ್ತು (and)  ಅಥವಾ (or)  ಅಲ್ಲ (not)

I/O:
  ಮುದ್ರಿಸು (print)   Print top of stack

Lists:
  [ ೧ ೨ ೩ ]         List literal
  ಉದ್ದ (length)      Length
  ನಕ್ಷೆ (map)        Map function
  ಸೋಸು (filter)     Filter
  ಮಡಿಸು (fold)      Fold/reduce

Commands:
  .s / stack        Show stack
  .w / words        Show defined words
  .v / vars         Show variables
  clear             Clear stack
  exit              Exit REPL
""")


def run_file(filename: str):
    """Run a Kapila file."""
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


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        run_file(sys.argv[1])
    else:
        repl()


if __name__ == "__main__":
    main()
