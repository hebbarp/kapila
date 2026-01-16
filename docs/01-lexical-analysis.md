# Phase 1: Lexical Analysis (The Lexer)

## What is Lexical Analysis?

Imagine you're reading a sentence:

> "The cat sat on the mat."

Your brain doesn't process this character by character. It groups characters into **words**: "The", "cat", "sat", etc. Then it processes the words.

A **lexer** (also called scanner or tokenizer) does the same for source code:

```
Input:  ಕಾರ್ಯ ಮುಖ್ಯ() { ಹಿಂತಿರುಗಿಸು ೦ }
Output: [KARYA, IDENT(ಮುಖ್ಯ), LPAREN, RPAREN, LBRACE, RETURN, NUMBER(0), RBRACE]
```

## Why Separate Lexing from Parsing?

Two reasons:

1. **Simplicity**: The parser doesn't need to worry about whitespace, comments, or how numbers are spelled. It just sees clean tokens.

2. **Efficiency**: Character-by-character analysis is different from structural analysis. Keeping them separate makes both simpler.

## The Theory: Regular Languages

Lexical analysis is based on **regular languages**—patterns that can be described by regular expressions or recognized by finite automata.

Examples of regular patterns:
- Identifier: `[ಅ-ಹa-zA-Z_][ಅ-ಹa-zA-Z0-9_]*`
- Number: `[0-9೦-೯]+`
- String: `"[^"]*"`

These patterns don't need to "remember" things or match nested structures. That's why a simple state machine (the lexer) can handle them.

## Token Types for Kapila

```python
class TokenType(Enum):
    # Literals
    NUMBER          # ೧೨೩, 123
    STRING          # "ನಮಸ್ಕಾರ"
    TRUE            # ನಿಜ
    FALSE           # ಸುಳ್ಳು

    # Identifiers and Keywords
    IDENTIFIER      # ಮುಖ್ಯ, x, ಸಂಖ್ಯೆ1
    KARYA           # ಕಾರ್ಯ (function)
    ADARE           # ಆದರೆ (if)
    ILLADIDDARE     # ಇಲ್ಲದಿದ್ದರೆ (else)
    HINDIRUGISU     # ಹಿಂತಿರುಗಿಸು (return)
    # ... more keywords

    # Operators
    PLUS            # +
    MINUS           # -
    STAR            # *
    SLASH           # /
    EQUAL           # =
    EQUAL_EQUAL     # ==
    LESS            # <
    GREATER         # >
    # ... more operators

    # Delimiters
    LPAREN          # (
    RPAREN          # )
    LBRACE          # {
    RBRACE          # }
    COMMA           # ,
    SEMICOLON       # ;

    # Special
    EOF             # End of file
    ERROR           # Lexical error
```

## The Lexer Algorithm

```
function nextToken():
    skip whitespace and comments

    if at end of input:
        return EOF token

    ch = current character

    if ch is letter (Kannada or ASCII):
        read entire word
        if word is keyword: return keyword token
        else: return identifier token

    if ch is digit (Kannada or ASCII):
        read entire number
        return number token

    if ch is '"':
        read until closing '"'
        return string token

    if ch is operator or delimiter:
        return appropriate token

    return error token
```

## Handling Kannada: The Challenge

English-based lexers have it easy. ASCII has clear boundaries:
- Letters: a-z, A-Z
- Digits: 0-9
- Everything else: operators, punctuation

Kannada is more complex:

1. **Conjuncts**: ಸ್ಕ is ONE logical unit (ಸ + ್ + ಕ = 3 codepoints)
2. **Matras**: ಕಾ is ಕ + ಾ (consonant + vowel sign)
3. **Variable-width**: Words don't have fixed character counts

Our solution: Use the Unicode module we adapted from Pampa. It knows which characters can appear in identifiers and how to classify them.

## Code Structure

```
src/lexer/
├── __init__.py      # Public API
├── tokens.py        # Token types and Token class
├── lexer.py         # The lexer implementation
└── keywords.py      # Kannada keyword mappings
```

## Key Insight: Keywords are Just Identifiers

Here's a common lexer trick:

1. Read all letters as one "word"
2. Look up the word in a keywords table
3. If found → return keyword token
4. If not found → return identifier token

```python
KEYWORDS = {
    'ಕಾರ್ಯ': TokenType.KARYA,
    'ಆದರೆ': TokenType.ADARE,
    'ಇಲ್ಲದಿದ್ದರೆ': TokenType.ILLADIDDARE,
    'ಹಿಂತಿರುಗಿಸು': TokenType.HINDIRUGISU,
    'ನಿಜ': TokenType.TRUE,
    'ಸುಳ್ಳು': TokenType.FALSE,
    # ...
}

def classify_word(word):
    return KEYWORDS.get(word, TokenType.IDENTIFIER)
```

## Error Handling

Good error messages are crucial. The lexer should track:
- **Line number**: Which line?
- **Column number**: Where in the line?
- **The problematic text**: What caused the error?

```
Error at line 5, column 12: Unterminated string
  | ಮುದ್ರಿಸು("ನಮಸ್ಕಾರ
  |          ^
```

## Testing the Lexer

Before moving to the parser, we should be able to:

```python
lexer = Lexer('ಕಾರ್ಯ ಮುಖ್ಯ() { ಹಿಂತಿರುಗಿಸು ೦ }')

for token in lexer:
    print(token)

# Output:
# Token(KARYA, 'ಕಾರ್ಯ', line=1, col=1)
# Token(IDENTIFIER, 'ಮುಖ್ಯ', line=1, col=7)
# Token(LPAREN, '(', line=1, col=12)
# Token(RPAREN, ')', line=1, col=13)
# Token(LBRACE, '{', line=1, col=15)
# Token(HINDIRUGISU, 'ಹಿಂತಿರುಗಿಸು', line=1, col=17)
# Token(NUMBER, '೦', line=1, col=28)
# Token(RBRACE, '}', line=1, col=30)
# Token(EOF, '', line=1, col=31)
```

## Next Steps

Once the lexer works, we move to [parsing](02-parsing.md) where tokens become trees.

## Exercises

1. Add support for comments (`//` single line, `/* */` multi-line)
2. Add hexadecimal numbers (`0x1F` or `೦x೧F`?)
3. Handle escape sequences in strings (`\n`, `\t`, `\"`)
4. Add support for character literals (`'ಅ'`)
