# Future: LLVM Backend

> **Status**: PLANNED - Not yet implemented

## Overview

A future version of Kapila may include an LLVM backend for direct native code generation without requiring a C compiler.

## Why LLVM?

```
Current:  Kapila → C Code → C Compiler → Native
Future:   Kapila → LLVM IR → LLVM → Native
```

### Benefits

| Feature | C Backend | LLVM Backend |
|---------|-----------|--------------|
| Optimization | Basic (-O2) | Advanced (-O3, LTO) |
| JIT Compilation | No | Yes |
| WebAssembly | No | Yes |
| Debug Info | Limited | Full DWARF |
| Cross-compilation | Manual | Built-in |

### Trade-offs

| Aspect | C Backend | LLVM Backend |
|--------|-----------|--------------|
| Distribution size | 18MB | 500MB+ |
| Build complexity | Simple | Complex |
| Dependencies | tcc/gcc | llvmlite + LLVM |
| Compilation speed | Fast | Slower |

## Proposed Architecture

```
┌─────────────────────────────────────────────────────┐
│                    kapilac                           │
├─────────────────────────────────────────────────────┤
│  ┌─────────┐   ┌─────────┐   ┌─────────────────┐   │
│  │ Parser  │ → │   AST   │ → │ Code Generator  │   │
│  └─────────┘   └─────────┘   └────────┬────────┘   │
│                                       │            │
│                    ┌──────────────────┼────────┐   │
│                    ▼                  ▼        │   │
│              ┌──────────┐      ┌──────────┐    │   │
│              │ C Backend│      │LLVM Back │    │   │
│              │ (current)│      │ (future) │    │   │
│              └────┬─────┘      └────┬─────┘    │   │
│                   │                 │          │   │
└───────────────────┼─────────────────┼──────────┘   │
                    ▼                 ▼
              ┌──────────┐      ┌──────────┐
              │ tcc/gcc  │      │   LLVM   │
              └────┬─────┘      └────┬─────┘
                   │                 │
                   ▼                 ▼
              ┌──────────┐      ┌──────────┐
              │   .exe   │      │.exe/.wasm│
              └──────────┘      └──────────┘
```

## LLVM IR Example

For the Kapila code:
```
೫ ೩ ಕೂಡು ಮುದ್ರಿಸು.
```

The LLVM IR would look like:
```llvm
define i32 @main() {
entry:
    ; push 5
    call void @push_int(i64 5)
    ; push 3
    call void @push_int(i64 3)
    ; add
    call void @add_op()
    ; print
    call void @println_op()

    call void @kapila_cleanup()
    ret i32 0
}
```

## Implementation Plan

### Phase 1: llvmlite Integration
- Add llvmlite dependency
- Create `src/codegen/llvm_generator.py`
- Generate basic LLVM IR for arithmetic

### Phase 2: Full Code Generation
- Function definitions
- Control flow (conditionals)
- Stack operations

### Phase 3: Optimization
- Enable LLVM optimization passes
- Implement tail-call optimization for recursion

### Phase 4: Additional Targets
- WebAssembly output
- JIT compilation for REPL

## Using llvmlite

```python
from llvmlite import ir, binding

# Create module
module = ir.Module(name="kapila_program")

# Define main function
func_type = ir.FunctionType(ir.IntType(32), [])
main = ir.Function(module, func_type, name="main")

# Generate IR
block = main.append_basic_block(name="entry")
builder = ir.IRBuilder(block)

# ... generate code ...

# Compile
binding.initialize()
binding.initialize_native_target()
target = binding.Target.from_default_triple()
target_machine = target.create_target_machine()
mod = binding.parse_assembly(str(module))
mod.verify()
```

## Command-Line Interface (Future)

```bash
# Use LLVM backend
kapilac program.kpl -r --backend=llvm

# Generate LLVM IR
kapilac program.kpl -o program.ll --emit=llvm-ir

# Generate WebAssembly
kapilac program.kpl -o program.wasm --target=wasm32
```

## Timeline

This is a future enhancement with no committed timeline. The current C backend serves the project's educational and practical goals well.

Contributors interested in LLVM integration are welcome to discuss on GitHub.
