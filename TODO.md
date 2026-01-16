# Kapila TODO

## Completed ✅

### Phase 0: Foundation
- [x] Project structure and documentation
- [x] Kannada Unicode handling (from Pampa)
- [x] Language design (Forth + Smalltalk + Perl hybrid)

### Phase 1: Lexer
- [x] Token types for Kapila syntax
- [x] Kannada identifier recognition
- [x] Kannada numeral support (೦-೯)
- [x] String literals with escapes
- [x] Comments (// and /* */)
- [x] Operators and delimiters

### Phase 2: Interpreter
- [x] Stack-based VM
- [x] Hybrid infix/postfix execution
- [x] Word definitions (name: body ॥)
- [x] Variables (name := value.)
- [x] Conditionals (? operator)
- [x] Built-in words (Kannada and English)
- [x] Blocks [ ] with parameters
- [x] Higher-order functions (map, filter, fold)
- [x] REPL for interactive testing

### Phase 3: Parser ✅
- [x] Define AST node types (src/parser/ast.py)
- [x] Recursive descent parser (src/parser/parser.py)
- [x] Expression parsing with precedence
- [x] Statement parsing (WordDef, VarAssign, ExprStmt)
- [x] Block/function parsing
- [x] Error recovery and messages

### Phase 4: Type System ✅
- [x] Define core types (src/semantic/types.py)
  - ಪೂರ್ಣಾಂಕ (Int), ದಶಮಾಂಶ (Float), ಸಂಖ್ಯೆ (Number)
  - ಪಠ್ಯ (String), ಬೂಲ್ (Bool), ಶೂನ್ಯ (Void)
  - ಪಟ್ಟಿ (List), ನಕ್ಷೆ (Map), ಖಂಡ (Block)
- [x] Type inference (type_from_value, common_type)
- [x] Type checking pass (src/semantic/checker.py)
- [x] Symbol table with builtin types

### Phase 5: C Code Generation ✅
- [x] C code generator (src/codegen/c_generator.py)
- [x] Stack-based runtime in C
- [x] Arithmetic, comparison, logic operations
- [x] Word definitions → C functions
- [x] Compiler script (kapilac.py)

## Future 🔮

### LLVM Backend (optional)
- [ ] Set up llvmlite
- [ ] Generate LLVM IR instead of C
- [ ] Direct native compilation

### Phase 6: Runtime Library
- [ ] Memory management
- [ ] Print functions
- [ ] String operations
- [ ] List operations
- [ ] File I/O

### Phase 7: Tooling
- [ ] Better error messages with Kannada
- [ ] Source maps for debugging
- [ ] VSCode extension (syntax highlighting)
- [ ] Package manager (optional)

## Future Ideas 💡

- WebAssembly target
- JIT compilation mode
- Debugger
- Standard library
- FFI (Foreign Function Interface)
- Concurrency primitives

## Technical Debt 🔧

- [ ] Comprehensive test suite
- [ ] Benchmarks
- [ ] Documentation for all modules
- [ ] CI/CD setup
