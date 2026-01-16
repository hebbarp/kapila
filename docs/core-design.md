# Kapila Core Design

## Philosophy

> **Forth's soul, Smalltalk's face, Perl's tongue, Clojure's heart**

- **Forth's soul**: Stack-based concatenative core. Simple. Composable.
- **Smalltalk's face**: Message-passing syntax that reads naturally.
- **Perl's tongue**: Pronouns and linguistic shortcuts for expressiveness.
- **Clojure's heart**: Immutable data, functional transformations.
- **Panini's mind**: Formal grammar, meta-rules, self-describing.

## The Stack: Foundation of Everything

At its core, Kapila is a stack machine. Every operation:
1. Takes values from the stack
2. Does something
3. Puts results back on the stack

```
೧೦ ।                    // Push 10 → Stack: [10]
೨೦ ।                    // Push 20 → Stack: [10, 20]
+ ।                     // Add     → Stack: [30]
ಮುದ್ರಿಸು ।               // Print   → Stack: [] (prints 30)
```

Or on one line:
```
೧೦ ೨೦ + ಮುದ್ರಿಸು ।       // 30
```

This is pure **concatenative** programming. Words (operations) compose by concatenation.

## Stack Manipulation Words

| Word | Kannada | Effect | Stack Before → After |
|------|---------|--------|---------------------|
| dup | ನಕಲು | duplicate top | [a] → [a a] |
| drop | ಬಿಡು | discard top | [a] → [] |
| swap | ಅದಲುಬದಲು | swap top two | [a b] → [b a] |
| over | ಮೇಲೆ | copy second | [a b] → [a b a] |
| rot | ತಿರುಗಿಸು | rotate three | [a b c] → [b c a] |

```
೫ ನಕಲು * ।              // 5 dup * → 25 (5 squared)
೧೦ ೨೦ ಅದಲುಬದಲು - ।      // 10 20 swap - → 10 (20 - 10)
```

## Message Syntax: Sugar Over Stack

Smalltalk-style messages are **syntactic sugar** that desugar to stack operations.

### Unary Messages
```
// Sugar:
೫ ವರ್ಗ ।

// Desugars to:
೫ ವರ್ಗ ।               // Same! Unary messages ARE postfix.
```

### Binary Messages
```
// Sugar:
೧೦ + ೫ ।

// Desugars to:
೧೦ ೫ + ।               // Push 10, push 5, add
```

### Keyword Messages
```
// Sugar:
ಪಟ್ಟಿ ೫ಕ್ಕೆ "ಅ" ಇಡು ।

// Desugars to:
ಪಟ್ಟಿ ೫ "ಅ" ಇಡು ।       // Push list, push 5, push "a", put
```

The suffixes (-ಕ್ಕೆ, -ಯಲ್ಲಿ, -ಯಿಂದ) are **visual markers** for readability, but the stack doesn't care.

## Pronouns: Perl's Gift

### ಅದು (adu) - "it" - The Topic

Like Perl's `$_`, `ಅದು` refers to the current topic (top of stack or iteration variable).

```
// Explicit:
ಪಟ್ಟಿ ಪ್ರತಿಯೊಂದಕ್ಕೂ { x | x ಮುದ್ರಿಸು } ।

// With pronoun (ಅದು is implicit):
ಪಟ್ಟಿ ಪ್ರತಿಯೊಂದಕ್ಕೂ { ಅದು ಮುದ್ರಿಸು } ।

// Even shorter (ಅದು implied when obvious):
ಪಟ್ಟಿ ಪ್ರತಿಯೊಂದಕ್ಕೂ { ಮುದ್ರಿಸು } ।
```

### ನೀನು (neenu) - "you" - Self Reference

Inside a definition, `ನೀನು` refers to the object/context being defined.

```
// Defining a "class" or prototype
ವೃತ್ತ: {
    ತ್ರಿಜ್ಯ              // radius field

    ವಿಸ್ತೀರ್ಣ: {         // area method
        ನೀನು ತ್ರಿಜ್ಯ ನಕಲು * π *
    }
}

// Usage:
ವೃತ್ತ ಹೊಸ → c ।
c ೫ ತ್ರಿಜ್ಯ: ।         // set radius to 5
c ವಿಸ್ತೀರ್ಣ ।           // → 78.54...
```

### ಅವು (avu) - "they" - Arguments

Like Perl's `@_`, `ಅವು` refers to all arguments passed.

```
ಮೊತ್ತ: {
    ಅವು + fold ।        // fold + over all arguments
}

೧ ೨ ೩ ೪ ೫ ಮೊತ್ತ ।      // → 15
```

### ಇಲ್ಲಿ (illi) - "here" - Current Context/Scope

```
ಇಲ್ಲಿ x ೧೦ ।           // Define x = 10 in current scope
```

## Blocks: First-Class Code

Blocks are anonymous functions. They're stack-to-stack transformers.

```
// Block that adds 1
{ ೧ + }

// Block with named parameter
{ x | x x * }          // square

// Apply a block with 'ಮಾಡು' (do)
೫ { ೧ + } ಮಾಡು ।       // → 6

// Or just juxtaposition works
೫ { ೧ + } ।            // → 6 (blocks auto-apply)
```

## Control Flow

Control flow uses blocks and messages to booleans.

### Conditionals

```
// ಆದರೆ (if) / ಇಲ್ಲದಿದ್ದರೆ (else)
x ೫ > { "ದೊಡ್ಡ" } { "ಚಿಕ್ಕ" } ಆದರೆ-ಇಲ್ಲದಿದ್ದರೆ ಮುದ್ರಿಸು ।

// Or with message syntax:
x ೫ > ಆದರೆ: { "ದೊಡ್ಡ" ಮುದ್ರಿಸು } ಇಲ್ಲದಿದ್ದರೆ: { "ಚಿಕ್ಕ" ಮುದ್ರಿಸು } ।

// Stack-style (Forth-like):
x ೫ > { "ದೊಡ್ಡ" ಮುದ್ರಿಸು } ಆದರೆ ।   // if-only, no else
```

### Loops

```
// ತನಕ (while)
{ x ೦ > } ತನಕ: {
    x ಮುದ್ರಿಸು
    x ೧ - → x
} ।

// ಸಾರಿ (times)
೧೦ ಸಾರಿ: { "ನಮಸ್ಕಾರ" ಮುದ್ರಿಸು } ।

// ಪ್ರತಿಯೊಂದಕ್ಕೂ (for-each)
[ ೧ ೨ ೩ ] ಪ್ರತಿಯೊಂದಕ್ಕೂ: { ಮುದ್ರಿಸು } ।

// ರಿಂದ-ವರೆಗೆ (from-to range)
೧ ರಿಂದ ೧೦ ವರೆಗೆ: { ಮುದ್ರಿಸು } ।
```

## Definitions

### Words (Functions)

```
// Define a word
ವರ್ಗ: { ನಕಲು * } ।

// Use it
೫ ವರ್ಗ ।               // → 25

// Word with explicit stack effect comment (Forth tradition)
// ( n -- n² )
ವರ್ಗ: { ನಕಲು * } ।
```

### Values (Immutable by default - Clojure's heart)

```
// Bind a value (immutable)
೪೨ → ಉತ್ತರ ।           // answer = 42

// Trying to rebind is an error in pure mode
// ೧೦ → ಉತ್ತರ ।        // Error! Already bound

// Mutable binding (explicit)
೧೦ →! x ।              // →! means mutable
x ೧ + →! x ।           // OK, x is now 11
```

## Data Structures

### Lists (Immutable)

```
[ ೧ ೨ ೩ ೪ ೫ ] → ಸಂಖ್ಯೆಗಳು ।

// Operations return NEW lists
ಸಂಖ್ಯೆಗಳು ೬ ಸೇರಿಸು ।    // → [1 2 3 4 5 6], original unchanged

// Access
ಸಂಖ್ಯೆಗಳು ೦ ನೇ ।        // → 1 (0-indexed)
ಸಂಖ್ಯೆಗಳು ಮೊದಲ ।       // → 1
ಸಂಖ್ಯೆಗಳು ಕೊನೆಯ ।       // → 5
```

### Maps (Dictionaries)

```
{ ಹೆಸರು: "ರಾಮ" ವಯಸ್ಸು: ೩೦ } → ವ್ಯಕ್ತಿ ।

// Access
ವ್ಯಕ್ತಿ ಹೆಸರು ।          // → "ರಾಮ"

// Update (returns new map)
ವ್ಯಕ್ತಿ { ವಯಸ್ಸು: ೩೧ } ವಿಲೀನ ।  // → { ಹೆಸರು: "ರಾಮ" ವಯಸ್ಸು: ೩೧ }
```

## Functional Composition (Clojure's Heart)

### Pipeline Operator →

```
// Left to right data flow
"ನಮಸ್ಕಾರ ಜಗತ್ತು"
    → ಉದ್ದ
    → ವರ್ಗ
    → ಮುದ್ರಿಸು ।        // prints 169 (13²)

// Same as:
"ನಮಸ್ಕಾರ ಜಗತ್ತು" ಉದ್ದ ವರ್ಗ ಮುದ್ರಿಸು ।
```

### Function Composition

```
// Compose two functions
{ ೧ + } { ೨ * } ∘ → f ।   // f = (x+1)*2

೫ f ।                     // → 12

// Or with names
ಒಂದು-ಕೂಡಿಸು: { ೧ + } ।
ಎರಡು-ಗುಣಿಸು: { ೨ * } ।

ಒಂದು-ಕೂಡಿಸು ಎರಡು-ಗುಣಿಸು ∘ → f ।
```

### Map, Filter, Reduce

```
[ ೧ ೨ ೩ ೪ ೫ ]
    { ವರ್ಗ } ನಕ್ಷೆ          // map: [1 4 9 16 25]
    { ೧೦ < } ಸೋಸು         // filter: [1 4 9]
    { + } ಮಡಿಸು ।          // reduce: 14
```

## Panini's Mind: Meta-Programming

Panini's Ashtadhyayi had rules that generated other rules. Kapila should support this.

### Quotation (Code as Data)

```
// Quote a word - don't execute, just push the word itself
'ವರ್ಗ → f ।             // f holds the word ವರ್ಗ, not its result

// Execute quoted code
f ಮಾಡು ।               // runs whatever f holds

// Introspection
'ವರ್ಗ ವಿವರ ।            // → information about the word
```

### Word Definition at Runtime

```
// Define a word programmatically
"ಘನ" { ನಕಲು ನಕಲು * * } ಹೊಸ-ಪದ ।   // cube = x * x * x

೩ ಘನ ।                  // → 27
```

### Grammar Rules (Future)

```
// This is aspirational - defining syntax transformations
// Like Panini's sutras

ಸೂತ್ರ "X ಚದರ" → "X ನಕಲು *" ।

೫ ಚದರ ।                 // → 25 (expands via rule)
```

---

## Complete Example: Factorial

```
// ಅಪವರ್ತನ (factorial)
ಅಪವರ್ತನ: {
    ನಕಲು ೧ ≤
    { ಬಿಡು ೧ }                    // base case: drop n, return 1
    { ನಕಲು ೧ - ಅಪವರ್ತನ * }        // n * factorial(n-1)
    ಆದರೆ-ಇಲ್ಲದಿದ್ದರೆ
} ।

೫ ಅಪವರ್ತನ ।              // → 120
```

## Complete Example: FizzBuzz

```
೧ ರಿಂದ ೧೦೦ ವರೆಗೆ: {
    ನಕಲು ೧೫ % ೦ = { ಬಿಡು "FizzBuzz" }
    { ನಕಲು ೩ % ೦ = { ಬಿಡು "Fizz" }
      { ನಕಲು ೫ % ೦ = { ಬಿಡು "Buzz" }
        { }  // keep number
        ಆದರೆ-ಇಲ್ಲದಿದ್ದರೆ }
      ಆದರೆ-ಇಲ್ಲದಿದ್ದರೆ }
    ಆದರೆ-ಇಲ್ಲದಿದ್ದರೆ
    ಮುದ್ರಿಸು
} ।
```

## Summary

| Aspect | Design Choice |
|--------|---------------|
| Core | Stack-based concatenative (Forth) |
| Syntax | Message-passing sugar (Smalltalk) |
| Data | Immutable by default (Clojure) |
| Expressiveness | Pronouns ಅದು/ನೀನು/ಅವು (Perl) |
| Statement end | `।` (Kannada danda) |
| Meta | Code as data, runtime word creation (Lisp/Panini) |
