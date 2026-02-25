# -*- coding: utf-8 -*-
"""
Verb Frame Registry
====================

Each verb declares its expected semantic slots in stack order
(first = deepest, last = top of stack).

Slots are (role, type_constraint) tuples.
  - role: semantic role name (ವಸ್ತು, ಗಮ್ಯ, ಸಾಧನ, ಸ್ಥಳ)
  - type_constraint: expected type tag, or '*' for any type

Also provides a noun→type map for resolving bare nouns as type hints.
"""

# Verb → list of (role, type_constraint) in stack order
VERB_FRAMES = {
    'ಕಳಿಸು':    [('ವಸ್ತು', '*'), ('ಗಮ್ಯ', 'ವ್ಯಕ್ತಿ')],       # send: object, recipient
    'ಓದು':      [('ವಸ್ತು', 'ಕಡತ')],                         # read: object(file)
    'ಬರೆ':      [('ವಸ್ತು', '*'), ('ಗಮ್ಯ', 'ಕಡತ')],           # write: content, dest(file)
    'ಮುದ್ರಿಸು':  [('ವಸ್ತು', '*')],                           # print: object
    'ತೆರೆ':      [('ವಸ್ತು', 'ಕಡತ')],                         # open: object(file)
    'ಅಳಿಸು':    [('ವಸ್ತು', '*')],                            # delete: object
    'ನಕಲು':     [('ವಸ್ತು', '*'), ('ಗಮ್ಯ', 'ಸ್ಥಳ')],          # copy: object, dest
    'ಹುಡುಕು':   [('ವಸ್ತು', '*'), ('ಸ್ಥಳ', '*')],             # search: object, location
}


# Noun → type tag mapping for resolving bare nouns as type hints
NOUN_TYPE_MAP = {
    'ಕಡತ':    'ಕಡತ',       # file
    'ವ್ಯಕ್ತಿ':  'ವ್ಯಕ್ತಿ',    # person
    'ಸಂದೇಶ':  'ಪಠ್ಯ',       # message → text
    'ಸಂಖ್ಯೆ':  'ಸಂಖ್ಯೆ',     # number
    'ಪಟ್ಟಿ':   'ಪಟ್ಟಿ',      # list
}


def infer_type(stem: str, value) -> str:
    """Infer a type tag from a stem word or a runtime value.

    Args:
        stem: The Kannada stem word (after vibhakti removal).
        value: The resolved runtime value.

    Returns:
        A type tag string.
    """
    # Check the noun→type map first
    if stem in NOUN_TYPE_MAP:
        return NOUN_TYPE_MAP[stem]

    # Fall back to Python type inference
    if isinstance(value, str):
        return 'ಪಠ್ಯ'       # text
    if isinstance(value, (int, float)):
        return 'ಸಂಖ್ಯೆ'     # number
    if isinstance(value, list):
        return 'ಪಟ್ಟಿ'      # list
    if isinstance(value, bool):
        return 'ಬೂಲಿಯನ್'   # boolean

    return '*'
