# The Journey of Building a Programming Language

## What is a Programming Language?

At its core, a programming language is a **formal notation** for expressing computation. But it's more than syntax—it's a way of thinking, a tool for thought.

When we write:

```python
if x > 5:
    print("big")
```

We're not talking to the computer. We're expressing an idea in a structured way that can be *mechanically transformed* into machine instructions.

## The Compilation Pipeline

Every compiler follows roughly the same path:

```
Source Text → Tokens → Tree → Validated Tree → Target Code
              (Lexer)  (Parser) (Semantic)      (CodeGen)
```

Let's understand each phase:

### Phase 1: Lexical Analysis (Lexer/Scanner)

**Question**: How do we break `"ಕಾರ್ಯ ಮುಖ್ಯ()"` into meaningful chunks?

The lexer reads characters and groups them into **tokens**:

```
Input:  ಕಾರ್ಯ ಮುಖ್ಯ()
Output: [KARYA, IDENTIFIER("ಮುಖ್ಯ"), LPAREN, RPAREN]
```

**Key concepts**:
- Regular expressions / finite automata
- Handling Unicode (essential for Kannada!)
- Keywords vs identifiers
- Whitespace and comments

### Phase 2: Parsing (Syntax Analysis)

**Question**: Is `ಕಾರ್ಯ ಮುಖ್ಯ()` grammatically valid? What structure does it represent?

The parser takes tokens and builds an **Abstract Syntax Tree (AST)**:

```
         FunctionDecl
        /     |      \
    name    params   body
      |       |        |
   "ಮುಖ್ಯ"    []      Block
```

**Key concepts**:
- Context-free grammars
- Recursive descent parsing
- Operator precedence
- Error recovery

### Phase 3: Semantic Analysis

**Question**: Does the program make sense? Are types correct?

```
ಸಂಖ್ಯೆ x = "hello"  // Error! Type mismatch
```

**Key concepts**:
- Symbol tables
- Type checking
- Scope resolution
- Name binding

### Phase 4: Code Generation

**Question**: How do we express this in LLVM IR?

```llvm
define i32 @main() {
entry:
    ret i32 0
}
```

**Key concepts**:
- Intermediate representations
- SSA form (Static Single Assignment)
- Register allocation (LLVM handles this)
- Calling conventions

## Why LLVM?

LLVM is a compiler infrastructure that provides:

1. **LLVM IR**: A typed, low-level intermediate representation
2. **Optimization passes**: Constant folding, dead code elimination, etc.
3. **Target code generation**: x86, ARM, RISC-V, WebAssembly...

By targeting LLVM IR, Kapila automatically gets:
- Native performance
- Cross-platform support
- World-class optimizations

## What Makes This Journey Special?

We're not just building *any* language—we're building a **Kannada** language.

Questions to explore:
- Can SOV (Subject-Object-Verb) word order influence syntax?
- Should operators be Kannada symbols or ASCII?
- Can agglutinative suffixes inspire new constructs?
- How do we handle Kannada numerals (೧, ೨, ೩)?

These questions don't have obvious answers. That's what makes this interesting.

## Next Steps

1. **[Lexical Analysis](01-lexical-analysis.md)**: Building the tokenizer
2. **[Parsing](02-parsing.md)**: Building the parser
3. **[Language Design](language-design.md)**: Exploring Kannada-influenced features
