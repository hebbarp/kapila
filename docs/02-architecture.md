# Kapila Architecture

## Overview

Kapila has two execution paths:

1. **Interpreter** (current) - for rapid prototyping and testing
2. **Compiler** (planned) - for native execution via LLVM

**Important**: Kapila does NOT translate to English. Kannada source is processed directly.

## Current: Interpreter

```
ಕನ್ನಡ Source Code
       │
       ▼
 ┌───────────┐
 │   Lexer   │   Breaks source into tokens
 └───────────┘   "೫ + ೧೦" → [NUM(5), PLUS, NUM(10)]
       │
       ▼
 ┌───────────┐
 │    VM     │   Stack-based virtual machine
 └───────────┘   Executes tokens directly in Python
       │
       ▼
    Result
```

### How the VM Works

The VM is a **stack machine**. Operations take values from a stack and push results back.

```
Input: 5 10 +

Step 1: push 5     Stack: [5]
Step 2: push 10    Stack: [5, 10]
Step 3: +          Stack: [15]  (pops 5 and 10, pushes 15)
```

### Hybrid Execution Model

Kapila uses Perl-style DWIM (Do What I Mean):

- **Top level**: Infix math works naturally
  ```
  5 * 10 + 3    // parsed as infix → 53
  ```

- **Inside blocks**: Pure postfix (Forth-style)
  ```
  square: dup * ॥   // dup and * are stack operations
  ```

### Word Lookup

When the VM sees a word like `ನಕಲು`:

1. Check if it's a built-in → execute Python function
2. Check if it's user-defined → execute the block
3. Check if it's a variable → push its value
4. Otherwise → error

No English translation occurs. The Kannada word directly maps to an operation.

## Planned: LLVM Compiler

```
ಕನ್ನಡ Source Code
       │
       ▼
 ┌───────────┐
 │   Lexer   │   Tokens
 └───────────┘
       │
       ▼
 ┌───────────┐
 │  Parser   │   Abstract Syntax Tree (AST)
 └───────────┘
       │
       ▼
 ┌───────────┐
 │ Semantic  │   Type checking, validation
 │ Analysis  │
 └───────────┘
       │
       ▼
 ┌───────────┐
 │  CodeGen  │   LLVM Intermediate Representation
 └───────────┘
       │
       ▼
 ┌───────────┐
 │   LLVM    │   Optimization passes
 │ Toolchain │   Native code generation
 └───────────┘
       │
       ▼
 Native Executable (x86, ARM, etc.)
```

### Why LLVM?

1. **No English dependency** - Kannada → LLVM IR → machine code
2. **Native performance** - compiled code runs at full speed
3. **Cross-platform** - LLVM targets x86, ARM, RISC-V, WebAssembly
4. **Optimization** - LLVM provides world-class optimizations

### LLVM IR Example

Kapila code:
```
square: dup * ॥
೫ square ಮುದ್ರಿಸು.
```

Would compile to LLVM IR like:
```llvm
define i64 @square(i64 %x) {
    %result = mul i64 %x, %x
    ret i64 %result
}

define i32 @main() {
    %1 = call i64 @square(i64 5)
    call void @print_i64(i64 %1)
    ret i32 0
}
```

Then LLVM compiles this to native machine code.

## Implementation Status

| Component | Status | Description |
|-----------|--------|-------------|
| Lexer | ✅ Complete | Tokenizes Kannada source |
| VM Interpreter | ✅ Complete | For testing and prototyping |
| Parser | 🔲 Planned | Build AST from tokens |
| Semantic Analysis | 🔲 Planned | Type checking, validation |
| LLVM CodeGen | 🔲 Planned | Generate LLVM IR |
| Runtime Library | 🔲 Planned | Print, I/O, memory management |

## File Structure

```
src/
├── unicode/       # Kannada character handling
│   └── kannada.py
├── lexer/         # Tokenization
│   ├── tokens.py
│   └── lexer.py
├── vm/            # Interpreter (current)
│   ├── vm.py
│   └── builtins.py
├── parser/        # AST construction (planned)
├── semantic/      # Type checking (planned)
└── codegen/       # LLVM generation (planned)
```

## Next Steps

1. **Parser**: Convert tokens to AST
2. **Type System**: Define Kapila's type system
3. **LLVM Bindings**: Use `llvmlite` for IR generation
4. **Runtime**: Implement print, memory, I/O in C/LLVM
5. **Optimization**: Leverage LLVM optimization passes
