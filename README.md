# ಕಪಿಲ (Kapila)

Kapila is an experimental multilingual, stack-based programming language with
Kannada at its center. It currently supports Kannada, Hindi (Devanagari),
Telugu, and English vocabulary, including each script's native numerals.

Kapila combines postfix execution with infix expressions and compiles programs
to native executables through a C backend. An experimental LLVM IR backend is
also included.

## Status

Kapila 0.8.0 is a functional alpha suitable for language experimentation and
compiler education.

- Interpreter and REPL: working
- Kannada, Hindi, and Telugu vocabulary: working
- Parser and AST: working
- Type analysis: basic and intentionally lenient
- C backend and native compilation: working
- C runtime for arithmetic, strings, lists, files, and higher-order words: working
- LLVM IR backend: experimental; variables, maps, lists, and conditionals are incomplete
- Web playground: direct execution, Kannada natural-language input, and experimental
  context-aware Sandarbha sessions
- Automated tests: `unittest` and `pytest` regression coverage, including all
  runnable examples and a native compiler smoke test

The implementation explicitly supports three Indic scripts today. Supporting
an additional language requires adding its Unicode rules and vocabulary; “any
language” is an extension goal rather than an automatic capability.

## Execution paths

```text
Source ──► Lexer ──► Python stack VM
   │
   └─────► Parser ──► AST ──► C ──► gcc/clang/tcc ──► native executable
                         │
                         └──► LLVM IR (experimental)
```

Kapila processes Indic source directly; users do not need to rewrite programs
with English keywords.

## Quick start

Requires Python 3.10 or newer.

```powershell
# Run a program with the interpreter
python kapila.py examples/hello.kpl

# Start the REPL
python kapila.py

# Compile and run natively (requires gcc, clang, or tcc)
python kapilac.py examples/hello.kpl -r

# Show generated C or LLVM IR
python kapilac.py examples/hello.kpl --emit-c
python kapilac.py examples/hello.kpl --emit-llvm

# Start the web playground
python app.py
```

## Example

```kapila
// Define a word
ವರ್ಗ: ನಕಲು * ॥

// Infix expression and postfix action
x := ೫ * ೨.
x ವರ್ಗ ಮುದ್ರಿಸು.    // prints 100

// Conditional
x > ೫ ? [ "ದೊಡ್ಡ" ಮುದ್ರಿಸು ] [ "ಚಿಕ್ಕ" ಮುದ್ರಿಸು ].
```

Equivalent arithmetic can use another supported vocabulary:

```kapila
५ ३ जोड़ो छापो.          // Hindi: 8
౫ ౩ కూడు ముద్రించు.      // Telugu: 8
```

## Tests

```powershell
python -m unittest discover -v
python -m pytest -q
```

`file_processor.kpl` is excluded from the automatic example run because it
requires a command-line filename. The other example programs are exercised by
the regression suite.

## Repository layout

```text
src/lexer/       tokenization
src/parser/      AST and recursive-descent parser
src/semantic/    types and type checker
src/vm/          interpreter and built-ins
src/codegen/     C and experimental LLVM backends
src/unicode/     Kannada, Devanagari, and Telugu handling
src/sandarbha/   experimental contextual role resolution
runtime/         C runtime
lib/             Kapila standard prelude
examples/        runnable programs
tests/           manual demonstrations and automated regressions
docs/            design and compiler notes
```

See [TODO.md](TODO.md) for the remaining roadmap.
