# Kapila Language Design: Thinking in Kannada

## The Central Question

> Can changing the natural language of programming change how we think about computation?

Most programming languages are designed by English speakers, with English-derived keywords and left-to-right, SVO (Subject-Verb-Object) thinking. What happens when we design from Kannada's perspective?

## Kannada Linguistic Features

### 1. Word Order: SOV vs SVO

**English (SVO)**: "I eat rice"
**Kannada (SOV)**: "ನಾನು ಅನ್ನವನ್ನು ತಿನ್ನುತ್ತೇನೆ" (I rice eat)

Most programming languages follow SVO patterns:
```python
x = compute(y)      # subject verb object
result = add(a, b)  # subject verb objects
```

**What if Kapila embraced SOV?**

```
// Traditional (SVO-like)
ಫಲಿತಾಂಶ = ಕೂಡಿಸು(ಅ, ಬ)

// SOV-inspired alternative
ಅ ಬ ಕೂಡಿಸು → ಫಲಿತಾಂಶ
```

This resembles **concatenative/stack-based** languages like Forth:
```forth
5 3 + .   \ prints 8
```

**Design Question**: Should Kapila support both styles? Or commit to one?

---

### 2. Agglutination: Suffixes that Transform Meaning

Kannada builds meaning through suffixes:

| Base | + Suffix | Meaning |
|------|----------|---------|
| ಮನೆ (house) | ಮನೆಯಲ್ಲಿ | in the house |
| ಮನೆ | ಮನೆಗೆ | to the house |
| ಮನೆ | ಮನೆಯಿಂದ | from the house |

**Programming analogy**: Method chaining or postfix operators

```
// Could suffixes modify operations?
ಸಂಖ್ಯೆಗಳು.ಒಟ್ಟು          // sum (ಒಟ್ಟು = total)
ಸಂಖ್ಯೆಗಳು.ಒಟ್ಟು.ಸರಾಸರಿಗೆ  // to average (suffix transforms)

// Or control flow?
ಕಾರ್ಯ.ಆದರೆ_ವಿಫಲವಾದರೆ(ಬ್ಯಾಕಪ್_ಕಾರ್ಯ)  // if_fails suffix
```

---

### 3. Verb Conjugation: Encoding Information in the Verb

Kannada verbs encode tense, person, number, and gender:

- ಮಾಡುತ್ತೇನೆ (I do/will do)
- ಮಾಡುತ್ತಾನೆ (He does)
- ಮಾಡಿದೆ (I did)
- ಮಾಡಿದನು (He did)

**Programming analogy**: Could function names encode execution semantics?

```
ಲೆಕ್ಕ.ಹಾಕು()      // compute now (imperative)
ಲೆಕ್ಕ.ಹಾಕುವ()    // will compute (lazy/deferred)
ಲೆಕ್ಕ.ಹಾಕಿದ()    // already computed (cached/memoized)
```

---

### 4. Compound Words (ಸಮಾಸ)

Kannada creates compound words extensively:
- ರಾಜ + ಮಾರ್ಗ = ರಾಜಮಾರ್ಗ (king's road, highway)
- ನೀರು + ಹಕ್ಕಿ = ನೀರುಹಕ್ಕಿ (water bird)

**Programming analogy**: Meaningful identifier composition

```
// Instead of camelCase or snake_case
ಕಡತಹೆಸರು      // file + name = filename
ಪಟ್ಟಿಉದ್ದ       // list + length
ವರ್ತುಲವಿಸ್ತೀರ್ಣ  // circle + area
```

---

### 5. Particles and Postpositions

Kannada uses particles that add nuance:
- ಏ (emphasis): ಅವನೇ ಬಂದ (HE came, emphatic)
- ಊ (also): ಅವನೂ ಬಂದ (He also came)
- ಅಲ್ಲ (negation): ಅವನು ಬಂದಿಲ್ಲ (He did not come)

**Programming analogy**: Operator modifiers

```
ಮುದ್ರಿಸು(x)         // print x
ಮುದ್ರಿಸು(x)ಊ        // also print x (side effect marker?)
ಮುದ್ರಿಸು(x)ಏ        // definitely print x (force evaluation?)
```

---

## Proposed Language Features

### Core Keywords (ಕೀಲಿಪದಗಳು)

| Kannada | Meaning | Usage |
|---------|---------|-------|
| ಕಾರ್ಯ | function/action | function definition |
| ಆದರೆ | but/if | conditional |
| ಇಲ್ಲದಿದ್ದರೆ | if not/else | else clause |
| ಆಗ | then | consequence |
| ಪುನರಾವರ್ತಿಸು | repeat | loop |
| ಪ್ರತಿಯೊಂದಕ್ಕೂ | for each | iteration |
| ತನಕ | until | while condition |
| ಹಿಂತಿರುಗಿಸು | return/give back | return value |
| ನಿಜ / ಸುಳ್ಳು | true / false | booleans |
| ಮತ್ತು / ಅಥವಾ | and / or | logical operators |
| ಅಲ್ಲ | not | negation |

### Types (ಬಗೆಗಳು)

| Kannada | Meaning | Maps to |
|---------|---------|---------|
| ಸಂಖ್ಯೆ | number | i64 / f64 |
| ಪೂರ್ಣಾಂಕ | integer | i64 |
| ದಶಮಾಂಶ | decimal | f64 |
| ಅಕ್ಷರ | letter/char | char |
| ಪಠ್ಯ | text | string |
| ನಿಜ/ಸುಳ್ಳು | true/false | bool |
| ಪಟ್ಟಿ | list | array |
| ಶೂನ್ಯ | void/nothing | void |

### Numerals

Support both ASCII and Kannada numerals:
```
ಸಂಖ್ಯೆ x = 42
ಸಂಖ್ಯೆ y = ೪೨    // same value!
```

| Kannada | Value |
|---------|-------|
| ೦ | 0 |
| ೧ | 1 |
| ೨ | 2 |
| ೩ | 3 |
| ೪ | 4 |
| ೫ | 5 |
| ೬ | 6 |
| ೭ | 7 |
| ೮ | 8 |
| ೯ | 9 |

---

## Sample Program Syntax

### Option A: Traditional (C-family inspired)

```
// ಪ್ರಧಾನ ಕಾರ್ಯ - main function
ಕಾರ್ಯ ಮುಖ್ಯ() {
    ಸಂಖ್ಯೆ x = ೧೦
    ಸಂಖ್ಯೆ y = ೨೦

    ಆದರೆ (x < y) {
        ಮುದ್ರಿಸು("x ಚಿಕ್ಕದು")
    } ಇಲ್ಲದಿದ್ದರೆ {
        ಮುದ್ರಿಸು("x ದೊಡ್ಡದು")
    }

    ಹಿಂತಿರುಗಿಸು ೦
}
```

### Option B: Kannada-native (SOV, agglutinative)

```
// ಮುಖ್ಯ ಕಾರ್ಯ - main function
ಮುಖ್ಯ ಕಾರ್ಯವು {
    x ಸಂಖ್ಯೆಯಾಗಿ ೧೦ ಇರಲಿ
    y ಸಂಖ್ಯೆಯಾಗಿ ೨೦ ಇರಲಿ

    x y ಗಿಂತ ಕಡಿಮೆಯಾದರೆ {
        "x ಚಿಕ್ಕದು" ಮುದ್ರಿಸು
    } ಇಲ್ಲದಿದ್ದರೆ {
        "x ದೊಡ್ಡದು" ಮುದ್ರಿಸು
    }

    ೦ ಹಿಂತಿರುಗಿಸು
}
```

### Option C: Hybrid (familiar structure, Kannada flavor)

```
ಕಾರ್ಯ ಮುಖ್ಯ() → ಸಂಖ್ಯೆ {
    x: ಸಂಖ್ಯೆ = ೧೦
    y: ಸಂಖ್ಯೆ = ೨೦

    ಆದರೆ x < y ಆಗ {
        ಮುದ್ರಿಸು("x ಚಿಕ್ಕದು")
    } ಇಲ್ಲದಿದ್ದರೆ {
        ಮುದ್ರಿಸು("x ದೊಡ್ಡದು")
    }

    ಹಿಂತಿರುಗಿಸು ೦
}
```

---

## Questions to Resolve

1. **Syntax style**: Traditional (A), Native (B), or Hybrid (C)?
2. **Operators**: Use ASCII (`+`, `-`, `<`) or Kannada symbols?
3. **String delimiters**: Use `"` or Kannada quotes `「」`?
4. **Semicolons**: Required, optional, or newline-terminated?
5. **Indentation**: Significant (like Python) or braces?
6. **Type position**: Before name (`ಸಂಖ್ಯೆ x`) or after (`x: ಸಂಖ್ಯೆ`)?

---

## Interesting Possibilities

### Pattern Matching with Case Suffixes

Kannada case suffixes could inspire pattern matching:

```
ಫಲಿತಾಂಶವನ್ನು ಪರಿಶೀಲಿಸು {
    ಯಶಸ್ವಿಯಾದರೆ(ಮೌಲ್ಯ) → ಮೌಲ್ಯವನ್ನು ಮುದ್ರಿಸು
    ವಿಫಲವಾದರೆ(ದೋಷ) → ದೋಷವನ್ನು ಮುದ್ರಿಸು
}
```

### Honorific Types

Kannada has respect levels in pronouns. Could types have "importance" levels?

```
ಮಹತ್ವದ_ಸಂಖ್ಯೆ secret_key = ...  // compiler enforces careful handling
```

### Poetic Comments

Since Kannada has rich poetic tradition, perhaps allow verse-style documentation:

```
/* ಕಂದ ಪದ್ಯ:
   ಕಪಿಲನ ಕೋಡಿನಲಿ
   ಗಣಕವು ಓದುತಲಿ
   ಕನ್ನಡ ನುಡಿಯಲಿ
   ಕ್ರಮವಿಧಿ ಬರೆಯಲಿ */
```

---

## Next Steps

1. Start with **Option A** (familiar to programmers)
2. Build working compiler
3. Experiment with B/C features in v2
4. Let the community guide evolution

The goal isn't to force Kannada grammar onto programming—it's to see what naturally emerges when we think in Kannada about computation.
