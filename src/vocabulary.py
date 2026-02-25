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
    # MATH - ಗಣಿತ ಕಾರ್ಯಗಳು
    # -------------------------------------------------------------------------
    'ಸಂಪೂರ್ಣ': 'abs',      # absolute value (sampurna)
    'ಕನಿಷ್ಠ': 'min',       # minimum (kanishta)
    'ಗರಿಷ್ಠ': 'max',       # maximum (garishta)
    'ಘಾತ': 'pow',          # power (ghata)
    'ವರ್ಗಮೂಲ': 'sqrt',     # square root (vargamula)
    'ನೆಲ': 'floor',        # floor (nela)
    'ಮೇಲ್ಮಿತಿ': 'ceil',    # ceiling (melmiti)
    'ಸುತ್ತು': 'round',      # round (suttu)

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
    'ಓದು': 'read',          # read (odu)
    'ಬರೆ': 'write',         # write (bare)

    # -------------------------------------------------------------------------
    # TYPE CONVERSION - ಪ್ರಕಾರ ಬದಲಾವಣೆ
    # -------------------------------------------------------------------------
    'ಪಠ್ಯಕ್ಕೆ': 'to-string',   # to string (pathyakke)
    'ಪೂರ್ಣಾಂಕಕ್ಕೆ': 'to-int',  # to integer (purnaankakke)
    'ದಶಮಾಂಶಕ್ಕೆ': 'to-float', # to float (dashamaanshakke)

    # -------------------------------------------------------------------------
    # LIST - ಪಟ್ಟಿ
    # -------------------------------------------------------------------------
    'ಉದ್ದ': 'length',       # length (udda)
    'ತೆಗೆ': 'nth',          # get at index (tege)
    'ಸೇರಿಸು': 'append',     # append (serisu)
    'ಮೊದಲ': 'first',        # first (modala)
    'ಕೊನೆ': 'last',         # last (kone)
    'ಉಳಿದ': 'rest',         # rest (ulida)
    'ತಿರುಗಿಸು': 'reverse',   # reverse (tirugisu)
    'ವಿಂಗಡಿಸು': 'sort',     # sort (vingadisu)
    'ಖಾಲಿಯೇ': 'is-empty',   # is empty? (khaliye)
    'ಪಟ್ಟಿಸೇರಿಸು': 'list-concat',  # list concat (pattiserisu)
    'ತೆಗೆದುಕೊ': 'take',     # take (tegeduko)
    'ಪಟ್ಟಿಬಿಡು': 'list-drop',  # drop from list (pattibidu)
    'ಇದೆಯೇ': 'list-contains', # contains? (ideye)
    'ಸ್ಥಾನ': 'index-of',    # index of (sthana)
    'ವ್ಯಾಪ್ತಿ': 'range',     # range (vyapti)
    'ಅನುಕ್ರಮ': 'iota',      # sequence/iota (anukrama)

    # -------------------------------------------------------------------------
    # STRING - ಪಠ್ಯ
    # -------------------------------------------------------------------------
    'ಜೋಡಿಸು': 'concat',     # concatenate (jodisu)
    'ವಿಭಜಿಸು': 'split',     # split (vibhajisu)
    'ಸೇರಿಸಿ': 'join',       # join (serisi)
    'ಭಾಗ': 'substring',     # substring (bhaga)
    'ಹುಡುಕು': 'find',       # find (huduku)
    'ಬದಲಿಸು': 'replace',    # replace (badalisu)
    'ಕತ್ತರಿಸು': 'trim',     # trim (kattarisu)
    'ಮೇಲಕ್ಕೆ': 'upper',     # uppercase (melakke)
    'ಕೆಳಕ್ಕೆ': 'lower',     # lowercase (kelakke)
    'ಆರಂಭವಾಗುತ್ತದೆ': 'starts-with',  # starts with (arambhavaaguttade)
    'ಕೊನೆಗೊಳ್ಳುತ್ತದೆ': 'ends-with',    # ends with (konegolluttade)
    'ಒಳಗೊಂಡಿದೆ': 'contains', # contains (olagondide)

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

    # -------------------------------------------------------------------------
    # CONTROL FLOW - ನಿಯಂತ್ರಣ
    # -------------------------------------------------------------------------
    'ತನಕ': 'while',         # while (tanaka)
    'ವರೆಗೆ': 'until',       # until (varege)
    'ಆದರೆ': 'if',           # if (adare)
    'ಆದರೆಇಲ್ಲ': 'if-else',   # if-else (adareillla)

    # -------------------------------------------------------------------------
    # CLI ARGUMENTS - ಆದೇಶ ಸಾಲಿನ ವಾದಗಳು
    # -------------------------------------------------------------------------
    'ವಾದಸಂಖ್ಯೆ': 'args-count',   # argument count (vadasankhye)
    'ವಾದ': 'args-get',             # get argument (vaada)

    # -------------------------------------------------------------------------
    # METAPROGRAMMING - ಮೆಟಾಪ್ರೋಗ್ರಾಮಿಂಗ್
    # -------------------------------------------------------------------------
    'ಮೌಲ್ಯಮಾಪನ': 'eval',           # eval (moulyamapana)
    'ಸಂಕೇತ': 'code-string',        # code-string (sanketha)
    'ರಚಿಸು': 'compose',            # compose (rachisu)
    'ಸೂತ್ರ': 'sutra',              # sutra
    'ಸ್ಮರಿಸು': 'smarisu',          # remember/invoke (smarisu)
    'ಸೂತ್ರಗಳು': 'list-sutras',     # list sutras (sutragalu)

    # =========================================================================
    # हिन्दी (HINDI) VOCABULARY
    # =========================================================================
    # Same builtins, Devanagari words. Same prosodic fingerprint.

    # ARITHMETIC - गणित
    'जोड़ो': '+',            # add (jodo)
    'घटाओ': '-',            # subtract (ghatao)
    'गुणा': '*',             # multiply (guna)
    'भाग': '/',              # divide (bhag) — note: also substring in Kannada
    'शेष': '%',              # modulo (shesh)

    # MATH - गणित कार्य
    'परिपूर्ण': 'abs',       # absolute (paripurna)
    'न्यूनतम': 'min',        # minimum (nyunatam)
    'अधिकतम': 'max',        # maximum (adhikatam)
    'घात': 'pow',            # power (ghaat)
    'वर्गमूल': 'sqrt',       # square root (vargamul)
    'फ़र्श': 'floor',        # floor (farsh)
    'छत': 'ceil',            # ceiling (chhat)
    'गोल': 'round',          # round (gol)

    # COMPARISON - तुलना
    'बराबर': '=',            # equal (barabar)
    'असमान': '!=',           # not equal (asamaan)
    'छोटा': '<',             # less than (chhota)
    'बड़ा': '>',              # greater than (bada)

    # LOGIC - तर्क
    'और': 'and',             # and (aur)
    'या': 'or',              # or (ya)
    'नहीं': 'not',           # not (nahin)

    # STACK - स्टैक
    'नकल': 'dup',            # duplicate (nakal)
    'हटाओ': 'drop',          # drop (hatao)
    'बदलो': 'swap',          # swap (badlo)
    'ऊपर': 'over',           # over (upar)
    'घुमाओ': 'rot',          # rotate (ghumao)

    # I/O - इनपुट/आउटपुट
    'छापो': 'print',         # print (chhapo)
    'पढ़ो': 'read',           # read (padho)
    'लिखो': 'write',         # write (likho)

    # TYPE CONVERSION
    'शब्दमें': 'to-string',  # to string
    'पूर्णांकमें': 'to-int', # to integer
    'दशमलवमें': 'to-float',  # to float

    # LIST - सूची
    'लंबाई': 'length',       # length (lambaai)
    'निकालो': 'nth',         # get at index (nikalo)
    'जोड़ना': 'append',      # append (jodna)
    'पहला': 'first',         # first (pehla)
    'आखिरी': 'last',         # last (aakhiri)
    'बाकी': 'rest',          # rest (baaki)
    'उलटो': 'reverse',       # reverse (ulto)
    'क्रमबद्ध': 'sort',      # sort (krambaddh)
    'खालीहै': 'is-empty',    # is empty (khali hai)
    'सूचीजोड़ो': 'list-concat',  # list concat
    'लो': 'take',            # take (lo)
    'छोड़ो': 'list-drop',    # drop from list (chhodo)
    'हैक्या': 'list-contains', # contains (hai kya)
    'स्थान': 'index-of',     # index of (sthan)
    'श्रेणी': 'range',       # range (shreni)
    'अनुक्रम': 'iota',       # sequence (anukram)

    # STRING - पाठ
    'जोड़': 'concat',        # concatenate (jod)
    'विभाजित': 'split',     # split (vibhajit)
    'मिलाओ': 'join',         # join (milao)
    'खंड': 'substring',      # substring (khand)
    'ढूँढो': 'find',         # find (dhundho)
    'बदलना': 'replace',      # replace (badalna)
    'काटो': 'trim',          # trim (kato)
    'बड़ाअक्षर': 'upper',    # uppercase
    'छोटाअक्षर': 'lower',   # lowercase

    # HIGHER-ORDER - उच्च क्रम
    'नक्शा': 'map',          # map (naksha)
    'छानो': 'filter',        # filter (chhano)
    'मोड़ो': 'fold',         # fold (modo)
    'हरएक': 'each',          # each (har ek)
    'बार': 'times',          # times (baar)
    'करो': 'do',             # do (karo)
    'बुलाओ': 'do',           # call (bulao) — alias

    # CONTROL FLOW - नियंत्रण
    'जबतक': 'while',         # while (jabtak)
    'तबतक': 'until',         # until (tabtak)
    'अगर': 'if',             # if (agar)
    'अगरनहीं': 'if-else',   # if-else (agar nahin)

    # METAPROGRAMMING - मेटाप्रोग्रामिंग
    'मूल्यांकन': 'eval',            # eval (mulyankan)
    'संकेत': 'code-string',         # code-string (sanket)
    'रचना': 'compose',              # compose (rachna)
    'सूत्र': 'sutra',               # sutra
    'स्मरण': 'smarisu',             # remember (smaran)
    'सूत्रसूची': 'list-sutras',      # list sutras (sutra-suchi)

    # =========================================================================
    # తెలుగు (TELUGU) VOCABULARY
    # =========================================================================
    # Same builtins, Telugu words. Same prosodic fingerprint.

    # ARITHMETIC - గణితం
    'కూడు': '+',            # add (koodu)
    'తీయు': '-',            # subtract (teeyu)
    'గుణించు': '*',         # multiply (guninchu)
    'భాగించు': '/',         # divide (bhaginchu)
    'శేషం': '%',            # modulo (shesham)

    # MATH - గణిత కార్యాలు
    'సంపూర్ణం': 'abs',      # absolute (sampurnam)
    'కనిష్ఠం': 'min',       # minimum (kanishtham)
    'గరిష్ఠం': 'max',       # maximum (garishtham)
    'ఘాతం': 'pow',          # power (ghatam)
    'వర్గమూలం': 'sqrt',     # square root (vargamulam)
    'అడుగు': 'floor',       # floor (adugu)
    'పైకప్పు': 'ceil',      # ceiling (paikappu)
    'సుమారు': 'round',      # round (sumaaru)

    # COMPARISON - పోలిక
    'సమానం': '=',           # equal (samanam)
    'అసమానం': '!=',         # not equal (asamanam)
    'చిన్నది': '<',          # less than (chinnadi)
    'పెద్దది': '>',          # greater than (peddadi)

    # LOGIC - తర్కం
    'మరియు': 'and',          # and (mariyu)
    'లేదా': 'or',            # or (leda)
    'కాదు': 'not',           # not (kadu)

    # STACK - స్టాక్
    'నకలు': 'dup',           # duplicate (nakalu)
    'వదులు': 'drop',         # drop (vadulu)
    'మార్చు': 'swap',        # swap (marchu)
    'పైన': 'over',           # over (paina)
    'తిప్పు': 'rot',         # rotate (tippu)

    # I/O - ఇన్‌పుట్/అవుట్‌పుట్
    'ముద్రించు': 'print',    # print (mudrinchu)
    'చదువు': 'read',         # read (chaduvu)

    # TYPE CONVERSION
    'పాఠ్యంగా': 'to-string',    # to string (pathyanga)
    'పూర్ణాంకంగా': 'to-int',    # to integer (purnankanga)
    'దశాంశంగా': 'to-float',    # to float (dashamshanga)

    # LIST - జాబితా
    'పొడవు': 'length',       # length (podavu)
    'తీసుకో': 'nth',         # get at index (teesuko)
    'చేర్చు': 'append',      # append (cherchu)
    'మొదటి': 'first',        # first (modati)
    'చివరి': 'last',         # last (chivari)
    'మిగిలిన': 'rest',       # rest (migilina)
    'తిరగేయు': 'reverse',    # reverse (tirageyu)
    'క్రమపరచు': 'sort',      # sort (kramaparachu)
    'ఖాళీనా': 'is-empty',    # is empty? (khalina)
    'జాబితాకలుపు': 'list-concat',  # list concat
    'తీసుకొను': 'take',      # take (teesukonu)
    'వదిలేయు': 'list-drop',  # drop from list (vadileyu)
    'ఉందా': 'list-contains', # contains? (unda)
    'స్థానం': 'index-of',    # index of (sthanam)
    'పరిధి': 'range',        # range (paridhi)
    'అనుక్రమం': 'iota',      # sequence (anukramam)

    # STRING - పాఠ్యం
    'కలుపు': 'concat',       # concatenate (kalupu)
    'విభజించు': 'split',     # split (vibhajinchu)
    'కలుపుము': 'join',       # join (kalupumu)
    'ఉపపాఠ్యం': 'substring', # substring (upapathyam)
    'వెతుకు': 'find',        # find (vethuku)
    'మార్పుచేయు': 'replace', # replace (marpucheyu)
    'కత్తిరించు': 'trim',    # trim (kattirinchu)
    'పెద్దఅక్షరం': 'upper',  # uppercase (peddaaksharam)
    'చిన్నఅక్షరం': 'lower',  # lowercase (chinnaaksharam)
    'మొదలవుతుంది': 'starts-with',  # starts with
    'చివరవుతుంది': 'ends-with',    # ends with
    'కలిగిఉంది': 'contains', # contains (kaligiundi)

    # HIGHER-ORDER - ఉన్నత క్రమం
    'మ్యాపు': 'map',          # map (myapu)
    'వడపోత': 'filter',       # filter (vadapotha)
    'మడత': 'fold',           # fold (madata)
    'ప్రతిదానికి': 'each',    # each (pratidaniki)
    'సార్లు': 'times',        # times (saarlu)
    'చేయి': 'do',            # do (cheyi)
    'పిలువు': 'do',          # call (piluvu) — alias

    # CONTROL FLOW - నియంత్రణ
    'అయ్యేవరకు': 'while',    # while (ayyevaraku)
    'వరకు': 'until',         # until (varaku)
    'అయితే': 'if',           # if (ayithe)
    'అయితేకాకపోతే': 'if-else', # if-else

    # METAPROGRAMMING - మెటాప్రోగ్రామింగ్
    'మూల్యాంకనం': 'eval',           # eval (mulyaankanam)
    'సంకేతం': 'code-string',        # code-string (sanketam)
    'రచించు': 'compose',            # compose (rachinchu)
    'సూత్రం': 'sutra',              # sutra (sutram)
    'స్మరించు': 'smarisu',          # remember (smarinchu)
    'సూత్రాలు': 'list-sutras',      # list sutras (sutraalu)
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

    # Hindi
    'सत्य': True,            # true (satya)
    'हाँ': True,             # yes (haan)
    'असत्य': False,          # false (asatya)
    'नहीं': False,           # no (nahin)
    'गलत': False,            # wrong (galat)

    # Telugu
    'నిజం': True,            # true (nijam)
    'అవును': True,           # yes (avunu)
    'అబద్ధం': False,         # false (abaddham)
    'కాదు': False,           # no (kadu)
    'తప్పు': False,          # wrong (tappu)
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
