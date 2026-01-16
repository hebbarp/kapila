# ಕಪಿಲ (Kapila)

A Kannada programming language that compiles to LLVM IR.

Named after **Kapila** (ಕಪಿಲ), the ancient Vedic sage who founded the Samkhya school of philosophy—one of the oldest systems of Indian philosophical inquiry that emphasized systematic enumeration and logical analysis.

## Vision

Previous attempts at Kannada programming languages translated Kannada keywords to English and used existing interpreters. Kapila takes a different approach:

- **Native compilation**: Kannada source → LLVM IR → Native machine code
- **Cultural authenticity**: Explore whether Kannada's grammatical structure can inspire new programming constructs
- **Educational**: Built as a learning journey through compiler construction

## Project Structure

```
kapila/
├── docs/                    # Educational documentation
│   ├── 00-overview.md       # The journey ahead
│   ├── 01-lexical-analysis.md
│   ├── 02-parsing.md
│   ├── 03-semantic-analysis.md
│   ├── 04-code-generation.md
│   └── language-design.md   # Exploring Kannada-influenced features
├── src/
│   ├── unicode/             # Kannada script handling (from Pampa)
│   ├── lexer/               # Tokenization
│   ├── parser/              # AST construction
│   ├── semantic/            # Type checking, symbol tables
│   ├── codegen/             # LLVM IR generation
│   └── kapila.py            # Main entry point
├── examples/                # Sample Kapila programs
├── tests/                   # Test suite
└── tools/                   # Helper utilities
```

## Building a Language: The Phases

```
┌─────────────────────────────────────────────────────────────────┐
│                     KAPILA COMPILATION PIPELINE                  │
└─────────────────────────────────────────────────────────────────┘

  ಕನ್ನಡ Source Code
        │
        ▼
  ┌───────────┐     "ಕಾರ್ಯ ಮುಖ್ಯ()" → [KARYA, IDENTIFIER, LPAREN, RPAREN]
  │   LEXER   │     Breaks source into tokens
  └───────────┘
        │
        ▼
  ┌───────────┐     Tokens → Abstract Syntax Tree
  │  PARSER   │     Understands grammar structure
  └───────────┘
        │
        ▼
  ┌───────────┐     Type checking, scope resolution
  │ SEMANTIC  │     Symbol table management
  │ ANALYSIS  │
  └───────────┘
        │
        ▼
  ┌───────────┐     AST → LLVM Intermediate Representation
  │  CODEGEN  │
  └───────────┘
        │
        ▼
  ┌───────────┐     LLVM IR → Native machine code
  │   LLVM    │     (handled by LLVM toolchain)
  └───────────┘
        │
        ▼
    Executable
```

## Current Status

✅ **Phase 1-2 Complete**: Lexer and Interpreter working
✅ **Phase 3 Complete**: Parser and AST construction
✅ **Phase 4 Complete**: Type system with Kannada type names
✅ **Phase 5 Complete**: C code generation

See [TODO.md](TODO.md) for detailed roadmap.

## Quick Start

```bash
# Start REPL
python kapila.py

# Run a file
python kapila.py examples/hello.kpl
```

## Example

```
// Define a word
square: dup * ॥

// Use it with infix math
x := ೫ * ೨.
x square ಮುದ್ರಿಸು.    // prints 100

// Conditional
x > ೫ ? [ "ದೊಡ್ಡ" ] [ "ಚಿಕ್ಕ" ] ಮುದ್ರಿಸು.
```

## Requirements

- Python 3.10+
- LLVM 15+ (for future compilation)
- llvmlite (Python bindings to LLVM)

## Acknowledgments

- Unicode handling adapted from [Pampa: AdiLipi](../pampa), a prosody analyzer for Indic scripts
