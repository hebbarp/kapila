# Kapila Syntax Exploration: Message-Passing + Kannada Grammar

## The Core Insight

Both Smalltalk and Kannada share a fundamental pattern: **the receiver comes before the action**.

| Language | Pattern | Example |
|----------|---------|---------|
| English | SVO | "I read the book" |
| C/Java | verb(object) | `read(book)` |
| **Kannada** | SOV | "ನಾನು ಪುಸ್ತಕವನ್ನು ಓದುತ್ತೇನೆ" (I book read) |
| **Smalltalk** | receiver message | `book read` |

This isn't coincidence—it's a different way of thinking about computation:
- C says: "Call the function `read` with argument `book`"
- Smalltalk/Kannada says: "Tell `book` to `read` itself" or "Act upon `book` by `read`ing"

## Smalltalk's Three Message Types

Smalltalk has three kinds of messages, ordered by precedence:

### 1. Unary Messages (no arguments)
```smalltalk
5 factorial          "→ 120"
'hello' size         "→ 5"
Date today           "→ current date"
```

### 2. Binary Messages (one argument, operator-like)
```smalltalk
3 + 4                "→ 7"
'hello', ' world'    "→ 'hello world'"
5 > 3                "→ true"
```

### 3. Keyword Messages (named arguments with colons)
```smalltalk
array at: 5                      "get element at index 5"
array at: 5 put: 'hello'         "put 'hello' at index 5"
string copyFrom: 1 to: 5         "substring from 1 to 5"
```

## Kannada Case Suffixes as Keywords

Kannada marks grammatical roles with suffixes:

| Suffix | Case | Meaning | Example |
|--------|------|---------|---------|
| -ಅನ್ನು (-annu) | Accusative | direct object | ಪುಸ್ತಕವನ್ನು (the book, as object) |
| -ಗೆ/-ಕ್ಕೆ (-ge/-kke) | Dative | to/for | ಅವನಿಗೆ (to him) |
| -ಯಿಂದ (-yinda) | Ablative | from/by | ಮನೆಯಿಂದ (from house) |
| -ಯಲ್ಲಿ (-alli) | Locative | in/at | ಮನೆಯಲ್ಲಿ (in house) |
| -ಯ (-ya) | Genitive | of/possessive | ಅವನ (his) |

These can become our keyword markers!

## Proposed Kapila Syntax

### Unary Messages
```
// Receiver followed by verb (no arguments)
೫ ವರ್ಗಮೂಲ              // 5 sqrt → 2.236...
"ನಮಸ್ಕಾರ" ಉದ್ದ          // "hello" length → 5
ಇಂದು ದಿನಾಂಕ             // today date → current date
ಪಟ್ಟಿ ಮೊದಲನೆಯದು         // list first → first element
```

### Binary Messages (Operators)
```
// Standard mathematical operators
೧೦ + ೫                  // → ೧೫
೧೦ - ೫                  // → ೫
೧೦ * ೫                  // → ೫೦
೧೦ / ೫                  // → ೨

// Comparison
೧೦ > ೫                  // → ನಿಜ (true)
೧೦ = ೧೦                 // → ನಿಜ
೧೦ ≠ ೫                  // → ನಿಜ

// String concatenation
"ನಮ" , "ಸ್ಕಾರ"           // → "ನಮಸ್ಕಾರ"
```

### Keyword Messages (Using Kannada Particles)

Instead of Smalltalk's colons, we use Kannada case suffixes or particles:

```
// Smalltalk: array at: 5 put: 'hello'
// Kapila:
ಪಟ್ಟಿಯಲ್ಲಿ ೫ನೇ ಸ್ಥಾನದಲ್ಲಿ "ನಮಸ್ಕಾರ" ಇಡು
// "in-list at-5th-position 'hello' put"

// Or shorter form with implicit markers:
ಪಟ್ಟಿ ೫ಕ್ಕೆ "ನಮಸ್ಕಾರ" ಇಡು
// "list to-5 'hello' put"

// Smalltalk: string copyFrom: 1 to: 5
// Kapila:
"ನಮಸ್ಕಾರ" ೧ರಿಂದ ೫ರವರೆಗೆ ತೆಗೆ
// "'hello' from-1 to-5 take"
```

### Assignment: The Flow Operator →

Instead of `=` or `:=`, use `→` to show value flowing into a name:

```
೧೦ → x                  // 10 flows into x
"ನಮಸ್ಕಾರ" → ಸಂದೇಶ        // "hello" flows into ಸಂದೇಶ (message)
೧೦ + ೨೦ → ಮೊತ್ತ          // 10 + 20 flows into ಮೊತ್ತ (sum)

// Reading: "Let 10 be x" or "10 becomes x"
```

### Blocks (Code Chunks)

Smalltalk uses `[ ]` for blocks. Kannada could use `{ }` with `|` for parameters:

```
// Block with no parameters
{ ಮುದ್ರಿಸು "ನಮಸ್ಕಾರ" }

// Block with one parameter
{ x | x + ೧ }

// Block with multiple parameters
{ x y | x + y }

// Using a block
೧ ರಿಂದ ೧೦ ವರೆಗೆ ಪ್ರತಿಯೊಂದಕ್ಕೂ { n | n ಮುದ್ರಿಸು }
// "from 1 to 10, for-each { n | n print }"
```

### Control Flow as Messages

Like Smalltalk, booleans receive messages:

```
// Smalltalk: (x > 5) ifTrue: [ ... ] ifFalse: [ ... ]
// Kapila:
(x > ೫) ಆದರೆ: { "ದೊಡ್ಡದು" ಮುದ್ರಿಸು } ಇಲ್ಲದಿದ್ದರೆ: { "ಚಿಕ್ಕದು" ಮುದ್ರಿಸು }

// Or more Kannada-natural:
x ೫ಕ್ಕಿಂತ ದೊಡ್ಡದಾದರೆ { "ದೊಡ್ಡದು" ಮುದ್ರಿಸು } ಇಲ್ಲದಿದ್ದರೆ { "ಚಿಕ್ಕದು" ಮುದ್ರಿಸು }
// "x if-greater-than-5 { print 'big' } else { print 'small' }"
```

### Loops as Messages

```
// While loop - send message to block
{ x > ೦ } ತನಕ: {
    x ಮುದ್ರಿಸು
    x - ೧ → x
}
// "while { x > 0 } do { print x; x - 1 → x }"

// Times loop
೧೦ ಸಾರಿ: { "ನಮಸ್ಕಾರ" ಮುದ್ರಿಸು }
// "10 times { print 'hello' }"

// Collection iteration
ಪಟ್ಟಿ ಪ್ರತಿಯೊಂದಕ್ಕೂ: { ಅಂಶ | ಅಂಶ ಮುದ್ರಿಸು }
// "list for-each { element | element print }"
```

### Method/Function Definition

```
// Define a method on a class/object
ಸಂಖ್ಯೆ ವರ್ಗ {
    ^ ತಾನು * ತಾನು        // ^ means return, ತಾನು means self
}

// Or standalone function style:
ವರ್ಗ: { x | x * x }
// "square: { x | x * x }"

// Calling:
೫ ವರ್ಗ                  // → ೨೫
```

### Classes and Objects

```
// Define a class
ವರ್ಗ ವ್ಯಕ್ತಿ {
    ಹೆಸರು               // instance variable
    ವಯಸ್ಸು              // instance variable

    // Method: greet
    ನಮಸ್ಕರಿಸು {
        "ನಮಸ್ಕಾರ, ನಾನು " , ಹೆಸರು , " ನನ್ನ ವಯಸ್ಸು " , ವಯಸ್ಸು ಮುದ್ರಿಸು
    }
}

// Create instance
ವ್ಯಕ್ತಿ ಹೊಸ → ರಾಮ
// "Person new → rama"

ರಾಮ ಹೆಸರು: "ರಾಮ"
ರಾಮ ವಯಸ್ಸು: ೩೦
ರಾಮ ನಮಸ್ಕರಿಸು
// Output: "ನಮಸ್ಕಾರ, ನಾನು ರಾಮ ನನ್ನ ವಯಸ್ಸು ೩೦"
```

---

## Complete Example: Fibonacci

```
// ಫಿಬೊನಾಚಿ ಸಂಖ್ಯೆ ಲೆಕ್ಕಹಾಕು
// Calculate Fibonacci number

ಫಿಬೊನಾಚಿ: { n |
    n ≤ ೧ ಆದರೆ: { ^ n }
    ^ (n - ೧) ಫಿಬೊನಾಚಿ + (n - ೨) ಫಿಬೊನಾಚಿ
}

// ಮುಖ್ಯ
೦ ರಿಂದ ೧೦ ವರೆಗೆ ಪ್ರತಿಯೊಂದಕ್ಕೂ { i |
    i ಫಿಬೊನಾಚಿ ಮುದ್ರಿಸು
}
```

## Complete Example: Hello World

```
// ಸರಳ - Simple
"ನಮಸ್ಕಾರ ಜಗತ್ತು!" ಮುದ್ರಿಸು
```

That's it. One line. The string receives the `ಮುದ್ರಿಸು` (print) message.

---

## Open Questions

1. **Precedence**: Smalltalk has unary > binary > keyword. Same for us?

2. **Statement separator**: Smalltalk uses `.` — what should Kapila use?
   - Newlines?
   - `. ` (period)?
   - `।` (Kannada danda)?

3. **Return**: Smalltalk uses `^`. Options:
   - `^` (familiar to Smalltalk users)
   - `↩` (Unicode return arrow)
   - `ಹಿಂತಿರುಗಿಸು` (explicit Kannada word)

4. **Self reference**: Smalltalk uses `self`. Kannada options:
   - `ತಾನು` (oneself, reflexive)
   - `ನಾನು` (I)
   - `ಇದು` (this)

5. **Method definition syntax**: How explicit should it be?

6. **Type annotations**: Optional? Required? Where?

---

## Why This Feels Right

1. **Reads naturally in Kannada**: "೫ ವರ್ಗ" reads as "5's square"
2. **SOV preserved**: Object comes before verb
3. **Suffixes are meaningful**: `-ಗೆ`, `-ಯಲ್ಲಿ`, `-ಯಿಂದ` mark roles
4. **Simple core**: Everything is just sending messages
5. **Composable**: Messages chain naturally

The syntax isn't forcing Kannada into C's mold—it's letting Kannada's structure guide the programming model.
