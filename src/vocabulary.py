# -*- coding: utf-8 -*-
"""
Kapila Vocabulary
=================

Central place to define Kannada word mappings.

To add new words:
1. Find the category (arithmetic, comparison, stack, etc.)
2. Add the Kannada word with its English equivalent
3. The word will automatically be available in the VM

Format: 'ಕನ್ನಡ': 'english_builtin'
"""

# =============================================================================
# VOCABULARY MAPPINGS
# =============================================================================
# Maps Kannada words to their English builtin equivalents.
# The English builtin must exist in builtins.py

VOCABULARY = {
    # -------------------------------------------------------------------------
    # ARITHMETIC - ಗಣಿತ
    # -------------------------------------------------------------------------
    'ಕೂಡು': '+',           # add (koodu)
    'ಕೂಡಿಸು': '+',         # addition (koodisu)
    'ಕಳೆ': '-',            # subtract (kale)
    'ಕಳೆಯಿರಿ': '-',        # subtraction (kaleyiri)
    'ಗುಣಿಸು': '*',         # multiply (gunisu)
    'ಗುಣಾಕಾರ': '*',        # multiplication (gunakaara)
    'ಭಾಗಿಸು': '/',         # divide (bhagisu)
    'ಭಾಗಾಕಾರ': '/',        # division (bhagakaara)
    'ಶೇಷ': '%',            # modulo/remainder (shesha)

    # -------------------------------------------------------------------------
    # COMPARISON - ಹೋಲಿಕೆ
    # -------------------------------------------------------------------------
    'ಸಮ': '=',             # equal (sama)
    'ಸಮನಲ್ಲ': '!=',        # not equal (samanalla)
    'ಕಿರಿದು': '<',         # less than (kiridu)
    'ಹಿರಿದು': '>',         # greater than (hiridu)
    'ಕಿರಿದುಸಮ': '<=',      # less than or equal (kiriduasama)
    'ಹಿರಿದುಸಮ': '>=',      # greater than or equal (hiriduasama)

    # -------------------------------------------------------------------------
    # BOOLEAN - ಬೂಲಿಯನ್
    # -------------------------------------------------------------------------
    # Note: These are handled specially in the parser/VM, not as builtins
    # 'ನಿಜ': True          # true (nija) - already in parser
    # 'ಸುಳ್ಳು': False       # false (sullu) - already in parser
    'ಸರಿ': 'true',         # true/correct (sari) - alias
    'ತಪ್ಪು': 'false',       # false/wrong (tappu) - alias
    'ಬೇಸ': 'false',        # no/false (besa) - alias

    # -------------------------------------------------------------------------
    # LOGIC - ತರ್ಕ
    # -------------------------------------------------------------------------
    'ಮತ್ತು': 'and',         # and (mattu)
    'ಅಥವಾ': 'or',          # or (athava)
    'ಅಲ್ಲ': 'not',          # not (alla)

    # -------------------------------------------------------------------------
    # STACK - ಸ್ಟಾಕ್
    # -------------------------------------------------------------------------
    'ನಕಲು': 'dup',          # duplicate (nakalu)
    'ಬಿಡು': 'drop',         # drop (bidu)
    'ಅದಲುಬದಲು': 'swap',     # swap (adalubadalu)
    'ಮೇಲೆ': 'over',         # over (mele)
    'ತಿರುಗಿಸು': 'rot',      # rotate (tirugisu)

    # -------------------------------------------------------------------------
    # I/O - ಇನ್‌ಪುಟ್/ಔಟ್‌ಪುಟ್
    # -------------------------------------------------------------------------
    'ಮುದ್ರಿಸು': 'print',    # print (mudhrisu)
    'ಓದು': 'read',          # read (odu) - future
    'ಬರೆ': 'write',         # write (bare) - future

    # -------------------------------------------------------------------------
    # LIST - ಪಟ್ಟಿ
    # -------------------------------------------------------------------------
    'ಉದ್ದ': 'length',       # length (udda)
    'ತೆಗೆ': 'nth',          # get at index (tege)
    'ಸೇರಿಸು': 'append',     # append (serisu)
    'ಮೊದಲ': 'first',        # first (modala)
    'ಕೊನೆ': 'last',         # last (kone) - future
    'ಉಳಿದ': 'rest',         # rest (ulida)

    # -------------------------------------------------------------------------
    # STRING - ಪಠ್ಯ
    # -------------------------------------------------------------------------
    'ಜೋಡಿಸು': ',',          # concatenate (jodisu)

    # -------------------------------------------------------------------------
    # HIGHER-ORDER - ಉನ್ನತ ಕ್ರಮಾಂಕ
    # -------------------------------------------------------------------------
    'ನಕ್ಷೆ': 'map',         # map (nakshe)
    'ಸೋಸು': 'filter',       # filter (sosu)
    'ಮಡಿಸು': 'fold',        # fold/reduce (madisu)
    'ಪ್ರತಿಯೊಂದಕ್ಕೂ': 'each', # each (pratiyondakku)
    'ಸಾರಿ': 'times',        # times (saari)
    'ಮಾಡು': 'do',           # do/execute (maadu)
    'ಕರೆ': 'do',            # call (kare) - alias for do
}


# =============================================================================
# BOOLEAN ALIASES
# =============================================================================
# These are special - they represent literal values, not operations

BOOLEAN_WORDS = {
    # True values
    'ನಿಜ': True,
    'true': True,
    'ಸರಿ': True,
    'ಹೌದು': True,          # yes (haudu)

    # False values
    'ಸುಳ್ಳು': False,
    'false': False,
    'ತಪ್ಪು': False,
    'ಬೇಸ': False,
    'ಇಲ್ಲ': False,          # no (illa)
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_all_kannada_words():
    """Return all Kannada vocabulary words."""
    return list(VOCABULARY.keys())


def get_english_equivalent(kannada_word: str) -> str:
    """Get English equivalent for a Kannada word."""
    return VOCABULARY.get(kannada_word)


def is_boolean_word(word: str) -> bool:
    """Check if word is a boolean literal."""
    return word in BOOLEAN_WORDS


def get_boolean_value(word: str) -> bool:
    """Get boolean value for a word."""
    return BOOLEAN_WORDS.get(word)


def print_vocabulary():
    """Print all vocabulary for reference."""
    print("ಕಪಿಲ ಶಬ್ದಕೋಶ (Kapila Vocabulary)")
    print("=" * 60)

    # Group by category
    categories = {}
    current_category = "Other"

    # Parse the VOCABULARY dict comments would be nice, but for now just print
    for kannada, english in sorted(VOCABULARY.items()):
        print(f"  {kannada:20} → {english}")


if __name__ == "__main__":
    print_vocabulary()
