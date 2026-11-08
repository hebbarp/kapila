# Compiler roadmap

**The plan: compile to C first, then bring in LLVM to compile directly.** C gets Kapila running natively with very little machinery. LLVM removes the C step later.

## Stage 1: through C (working)

```
Kapila source → parser → AST → C code → gcc, clang or TinyCC → executable
```

- The C generator is `src/codegen/c_generator.py`, and the runtime it links against is in `runtime/`.
- The Windows zip bundles TinyCC, so nobody has to install a C compiler.
- Try it with `kapilac myprog.kpl -r`.

The compiler has one firm rule: **it builds what you wrote or it refuses, with the line number.** It used to skip words it didn't know, so a compiled program could print the wrong answer with no warning.

## Stage 2: LLVM (experimental)

```
Kapila source → parser → AST → LLVM IR → machine code
```

LLVM's own bytecode format is called *bitcode* (`.bc`). From IR, LLVM can write bitcode, produce a native object file, or run the code straight away through its JIT. Any of those removes the need for a C compiler.

The generator is `src/codegen/llvm_generator.py`, and `kapilac myprog.kpl --emit-llvm` prints its output.

- [x] Set up llvmlite
- [x] Generate basic LLVM IR
- [ ] Correct variable storage and lookup
- [ ] Correct conditional control flow
- [ ] List and map runtime representation
- [ ] Direct native compilation

C remains the default until the LLVM backend passes everything on the [build status](Build-Status) page.

## What each engine can do

| Feature | Interpreter | Compiled through C | LLVM |
|---|---|---|---|
| Arithmetic, strings, words you define | yes | yes | partly |
| Variables with `:=` | yes | yes | not reliable yet |
| Lists, `ನಕ್ಷೆ`, `ಸೋಸು`, loops | yes | yes | not yet |
| Records `{ … }` | yes | refused | not yet |
| News, weather, Wikipedia | yes | refused | not yet |
| Sandarbha (context) words | yes | refused | not yet |

## Open decision

**What should compiling mean for live data?** The interpreter has picked up news, weather, Wikipedia and records, and the compiler has none of them. There are two ways forward:

1. Add records and HTTP to the C runtime. Compiled programs stay small and native, but it is real work, and each new source has to be written twice.
2. Have a compiled program carry the interpreter for those parts. It is quicker and only has to be written once, but the executables get larger and less truly native.
