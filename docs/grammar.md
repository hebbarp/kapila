# ಕಪಿಲ ವ್ಯಾಕರಣ — Kapila Grammar Map

**Goal:** a Kannada sentence *is* the program. Every common programming construct
gets the form Kannada grammar already uses for that idea, so the same sentence
always compiles to the same program. There is no statistical guessing.

Why Kannada fits:

- **The verb comes last** (subject–object–verb), so `ಐದು ಮೂರು ಕೂಡು` is already postfix. That suits Kapila's Forth-style stack.
- **Case endings (ವಿಭಕ್ತಿ) mark each noun's role** (object, instrument, destination, location). Arguments can then be identified by their role instead of their position.
- **Verb endings carry control flow**: conditional *-ಅರೆ* (if), *-ವವರೆಗೆ* (until), concessive *-ಆದರೂ* (even if), and the conjunctive participle *-ಇ* (do X, then …).
- **Ordinals (-ನೇ) and the question word ಎಷ್ಟನೇ** ("the how-many-th") give enumeration.

> Status: **draft, 2026-11-08.** All the forms in the table are proposals.
> The Hindi and Telugu columns in particular need review by a native speaker.

**Today column:** ✅ works in the VM now (verified) · 🟡 partial (reserved word only, or a different form) · ❌ not yet

---

## 1. Values and names

| Construct | Kannada form | Example | Hindi | Telugu | Today |
|---|---|---|---|---|---|
| Number literal | digits or number words | `೧೨` / ಹನ್ನೆರಡು | १२ / बारह | ౧౨ / పన్నెండు | ✅ digits · ❌ number words |
| Text literal | quotes | `"ನಮಸ್ಕಾರ"` | `"नमस्ते"` | `"నమస్కారం"` | ✅ |
| True / false | ನಿಜ / ಸುಳ್ಳು | | सत्य / असत्य | నిజం / అబద్ధం | ✅ |
| Nothing (null) | ಏನೂ ಇಲ್ಲ / ಶೂನ್ಯ | | कुछ नहीं | ఏమీ లేదు | 🟡 type keyword only |
| Bind (let) | X … ಆಗಿರಲಿ | x ಹತ್ತು ಆಗಿರಲಿ | x दस हो | x పది గా ఉండనీ | ✅ `x := ೧೦.` · 🟡 ಇರಲಿ reserved |
| Update | X-ಅನ್ನು … ಮಾಡು | x ಅನ್ನು ಹನ್ನೊಂದು ಮಾಡು | x को ग्यारह करो | x ని పదకొండు చేయి | ✅ `x := …` |
| Constant | ಸ್ಥಿರ | ಸ್ಥಿರ ಪೈ ೩.೧೪ | स्थिर | స్థిరం | ❌ |
| Scope | ಒಳಗೆ (inside a block) | | | | ❓ undecided |

## 2. Data

| Construct | Kannada form | Example | Hindi | Telugu | Today |
|---|---|---|---|---|---|
| List | ಪಟ್ಟಿ | `[ ೧ ೨ ೩ ]` | सूची | జాబితా | ✅ |
| Map / dictionary / record | **ಕೋಶ** (as in ಶಬ್ದಕೋಶ) | `{ ಲೇಖಕ: "ಕುವೆಂಪು" }` · ಪುಸ್ತಕದ ಲೇಖಕ | कोश | కోశం | ✅ literal, ಪಡೆ/ಇಡು/ಕೀಲಿಗಳು, genitive field access (2026-11-08) · ❌ the word ಕೋಶ |
| Set | ಗಣ | | समुच्चय | సమితి | ❌ |
| Pair / tuple | ಜೋಡಿ | | जोड़ा | జత | ❌ |
| Record | ದಾಖಲೆ | | अभिलेख | రికార్డు | ❌ |
| Enumerated type | ವಿಧಗಳು | ಬಣ್ಣದ ವಿಧಗಳು: ಕೆಂಪು, ಹಸಿರು | प्रकार | రకాలు | ❌ |

## 3. Operations

| Construct | Kannada form | Example | Hindi | Telugu | Today |
|---|---|---|---|---|---|
| Arithmetic | ಕೂಡು ಕಳೆ ಗುಣಿಸು ಭಾಗಿಸು ಶೇಷ | ಐದು ಮತ್ತು ಮೂರನ್ನು ಕೂಡು | जोड़ो घटाओ गुणा भाग | కూడు తీయు గుణించు భాగించు | ✅ |
| Comparison | **-ಕ್ಕಿಂತ / -ಗಿಂತ** + ದೊಡ್ಡದು / ಚಿಕ್ಕದು | x ಐದಕ್ಕಿಂತ ದೊಡ್ಡದು | x पाँच से बड़ा | x ఐదు కంటే పెద్దది | ✅ ಹಿರಿದು / ಕಿರಿದು · ❌ case-ending form |
| Equality | **-ಗೆ / -ಕ್ಕೆ ಸಮ** | x ಐದಕ್ಕೆ ಸಮ | x पाँच के बराबर | x ఐదుకు సమానం | ✅ ಸಮ |
| Logic | ಮತ್ತು ಅಥವಾ ಅಲ್ಲ | | और या नहीं | మరియు లేదా కాదు | ✅ |
| Indexing | **genitive + ordinal** | ಪಟ್ಟಿಯ ಮೂರನೇ ಅಂಶ | सूची का तीसरा | జాబితాలో మూడవది | ✅ ತೆಗೆ (nth) · ❌ natural form |
| Slicing | -ಇಂದ … -ವರೆಗೆ on ordinals | ಎರಡನೆಯದರಿಂದ ಐದನೆಯದರವರೆಗೆ | दूसरे से पाँचवें तक | రెండవ నుండి ఐదవ వరకు | 🟡 ಭಾಗ (text), ತೆಗೆದುಕೊ / ಪಟ್ಟಿಬಿಡು |
| Join text | ಜೋಡಿಸು | | जोड़ | కలుపు | ✅ |

## 4. Sequence

| Construct | Kannada form | Example | Hindi | Telugu | Today |
|---|---|---|---|---|---|
| Statement order | sentence end `.` / ನಂತರ | | फिर | తర్వాత | ✅ `.` |
| **Pipeline** | **conjunctive participle -ಇ** | ಓದಿ, ಸೋಸಿ, ವಿಂಗಡಿಸಿ, ಮುದ್ರಿಸು | पढ़कर, छानकर, छापो | చదివి, వడపోసి, ముద్రించు | ❌ (key construct) |
| Block | `[ … ]` | | | | ✅ |

## 5. Choice

| Construct | Kannada form | Example | Hindi | Telugu | Today |
|---|---|---|---|---|---|
| If | **conditional -ಅರೆ** on the verb | x ಐದಕ್ಕಿಂತ ದೊಡ್ಡದಾದರೆ "ದೊಡ್ಡದು" ಮುದ್ರಿಸು | अगर … तो | -తే (అయితే) | ✅ ಆದರೆ (postfix), `?` |
| Else | ಇಲ್ಲದಿದ್ದರೆ | … ಇಲ್ಲದಿದ್ದರೆ "ಚಿಕ್ಕದು" ಮುದ್ರಿಸು | नहीं तो | లేకపోతే | 🟡 VM runs ಆದರೆಇಲ್ಲ; ಇಲ್ಲದಿದ್ದರೆ reserved only |
| Else-if chain | ಇಲ್ಲದಿದ್ದರೆ … -ಅರೆ | | नहीं तो अगर | లేకపోతే … -తే | ❌ |
| Switch / match | X ಯಾವುದು ಎಂದು ನೋಡಿ: ೧ ಆದರೆ …, ೨ ಆದರೆ … | | x क्या है, देखो: | x ఏమిటో చూసి: | ❌ |
| Inline if (ternary) | same as if/else, inside an expression | | | | 🟡 `?` |
| Guard / early exit | -ಅರೆ … ಇಲ್ಲಿಯೇ ನಿಲ್ಲಿಸು | x ಶೂನ್ಯವಾದರೆ ಇಲ್ಲಿಯೇ ನಿಲ್ಲಿಸು | यहीं रुको | ఇక్కడే ఆపు | ❌ |

## 6. Repetition

| Construct | Kannada form | Example | Hindi | Telugu | Today |
|---|---|---|---|---|---|
| While | **-ಇರುವ ತನಕ** | x ಹತ್ತಕ್ಕಿಂತ ಚಿಕ್ಕದಿರುವ ತನಕ … | जब तक … तब तक | -ఉన్నంత వరకు | ✅ `[cond] [body] ತನಕ` |
| Until | **-ಉವವರೆಗೆ** | ಪಟ್ಟಿ ಖಾಲಿಯಾಗುವವರೆಗೆ … | … होने तक | -అయ్యేవరకు | ✅ ವರೆಗೆ |
| Counted (N times) | X ಸಲ / ಸಾರಿ | ಮೂರು ಸಲ "ಹ" ಮುದ್ರಿಸು | तीन बार | మూడు సార్లు | ✅ ಸಾರಿ |
| Range | **-ಇಂದ … -ವರೆಗೆ** | ಒಂದರಿಂದ ಹತ್ತರವರೆಗೆ | एक से दस तक | ఒకటి నుండి పది వరకు | ✅ ವ್ಯಾಪ್ತಿ (excludes the end; see issue 7) |
| For each | **ಪ್ರತಿಯೊಂದಕ್ಕೂ** (dative) | ಪ್ರತಿಯೊಂದಕ್ಕೂ ಮುದ್ರಿಸು | हर एक के लिए | ప్రతి దానికీ | ✅ |
| **Enumerate** | ordinals; **ಎಷ್ಟನೆಯದು**; sociative **-ಒಂದಿಗೆ** ("with") | ಪ್ರತಿಯೊಂದನ್ನೂ ಅದರ ಸ್ಥಾನದೊಂದಿಗೆ ಮುದ್ರಿಸು | अपने स्थान के साथ | దాని స్థానంతో | ❌ |
| Zip | -ಒಂದಿಗೆ ಜೊತೆಮಾಡು | ಹೆಸರುಗಳನ್ನು ಅಂಕಗಳೊಂದಿಗೆ ಜೊತೆಮಾಡು | … के साथ जोड़ो | … తో జతచేయి | ❌ |
| Infinite loop | ಯಾವಾಗಲೂ / ಪುನರಾವರ್ತಿಸು | | हमेशा / दोहराओ | ఎల్లప్పుడూ | 🟡 `loop` has no Kannada word and can't be stopped (no break) |
| Break | ನಿಲ್ಲಿಸು | | रोको | ఆపు | 🟡 reserved only |
| Continue | (ಇದನ್ನು ಬಿಟ್ಟು) ಮುಂದುವರಿಸು | | जारी रखो | కొనసాగించు | 🟡 reserved only |
| Nested loops | nesting | | | | ✅ |
| Recursion | a word that calls itself | `ಫ್ಯಾ: ನಕಲು ೧ > [ ನಕಲು ೧ - ಫ್ಯಾ * ] ಆದರೆ ॥` | | | ✅ (5! = 120 verified) |

## 7. Working on whole collections

| Construct | Kannada form | Example | Hindi | Telugu | Today |
|---|---|---|---|---|---|
| Map (transform each) | **ಪ್ರತಿಯೊಂದನ್ನೂ** (accusative) + verb | ಪ್ರತಿಯೊಂದನ್ನೂ ಎರಡರಿಂದ ಗುಣಿಸು | हर एक को … करो | ప్రతి దానినీ … చేయి | ✅ ನಕ್ಷೆ |
| **Filter (keep matching)** | **ಸೋಸು** | ಐದಕ್ಕಿಂತ ದೊಡ್ಡವುಗಳನ್ನು ಸೋಸು | छानो | వడపో | ✅ ಸೋಸು |
| Reject (remove matching) | ಹೊರಗಿಡು | ಸೊನ್ನೆಗಳನ್ನು ಹೊರಗಿಡು | बाहर रखो | బయట ఉంచు | ❌ |
| Reduce / fold | ಎಲ್ಲವನ್ನೂ + verb | ಎಲ್ಲವನ್ನೂ ಕೂಡು | सब जोड़ो | అన్నీ కలుపు | ✅ ಮಡಿಸು |
| Sum | ಮೊತ್ತ | ಪಟ್ಟಿಯ ಮೊತ್ತ | कुल | మొత్తం | ❌ (use ಮಡಿಸು) |
| Count | ಎಣಿಸು / ಎಷ್ಟು | ದೊಡ್ಡವು ಎಷ್ಟು ಇವೆ | गिनो / कितने | లెక్కించు / ఎన్ని | 🟡 ಉದ್ದ (length) |
| Min / max | ಕನಿಷ್ಠ / ಗರಿಷ್ಠ | | न्यूनतम / अधिकतम | కనిష్ఠం / గరిష్ఠం | ✅ |
| Search (first match) | **ಶೋಧಿಸು** | ಐದಕ್ಕಿಂತ ದೊಡ್ಡ ಮೊದಲನೆಯದನ್ನು ಶೋಧಿಸು | खोजो | వెతుకు | ❌ (ಹುಡುಕು = position in text) |
| Any | ಯಾವುದಾದರೂ … ಇದೆಯೇ | ಯಾವುದಾದರೂ ಸೊನ್ನೆ ಇದೆಯೇ | कोई भी … है? | ఏదైనా … ఉందా | 🟡 ಇದೆಯೇ (contains) |
| All | ಎಲ್ಲವೂ … ಆಗಿವೆಯೇ | ಎಲ್ಲವೂ ಧನಾತ್ಮಕವಾಗಿವೆಯೇ | सभी … हैं? | అన్నీ … నా | ❌ |
| Sort | ವಿಂಗಡಿಸು | | क्रम से लगाओ | క్రమపరచు | ✅ |
| Group by | -ಅನುಸಾರ ಗುಂಪು ಮಾಡು | ಬಣ್ಣದನುಸಾರ ಗುಂಪು ಮಾಡು | … के अनुसार समूह बनाओ | … ప్రకారం గుంపు చేయి | ❌ |
| Comprehension | covered by the participle pipeline (§4) | | | | ❌ |

## 8. Abstraction

| Construct | Kannada form | Example | Hindi | Telugu | Today |
|---|---|---|---|---|---|
| Define a function | **X ಎಂದರೆ …** | ವರ್ಗ ಎಂದರೆ ನಕಲು ಗುಣಿಸು | X मतलब … | X అంటే … | ✅ `ವರ್ಗ: ನಕಲು * ॥` · 🟡 ಕಾರ್ಯ reserved |
| Parameters | ಆಗಿ | `[ x ಆಗಿ x x * ]` | | | ✅ |
| Return | ಹಿಂತಿರುಗಿಸು (or implicit: top of the stack) | | लौटाओ | తిరిగి ఇవ్వు | 🟡 reserved only; the stack result is implicit |
| **Named arguments** | **case endings mark roles**, so order doesn't matter | ಪಟ್ಟಿಯನ್ನು ಎರಡರಿಂದ ಭಾಗಿಸು = ಎರಡರಿಂದ ಪಟ್ಟಿಯನ್ನು ಭಾಗಿಸು | को / से / में | ని / తో / లో | 🟡 sandarbha (experimental) |
| Lambda | `[ … ]` | | | | ✅ |
| Higher-order functions | blocks as values | | | | ✅ |
| Import a module | ತರು | ಗಣಿತವನ್ನು ತರು | लाओ | తెచ్చు | ❌ (only `lib/prelude.kpl`, loaded automatically) |

## 9. Errors

| Construct | Kannada form | Example | Hindi | Telugu | Today |
|---|---|---|---|---|---|
| Try | ಪ್ರಯತ್ನಿಸು | | कोशिश करो | ప్రయత్నించు | ❌ |
| Catch | **-ಅಲು ಆಗದಿದ್ದರೆ** | ಕಡತ ಓದಲು ಆಗದಿದ್ದರೆ "ಇಲ್ಲ" ಮುದ್ರಿಸು | … न हो पाए तो | … కాకపోతే | ❌ |
| Finally | **ಏನೇ ಆದರೂ** (concessive) | | जो भी हो | ఏమైనా సరే | ❌ |
| Raise | ದೋಷವೆಂದು ನಿಲ್ಲಿಸು | | त्रुटि कहकर रोको | దోషమని ఆపు | ❌ |
| Assert | ಖಚಿತಪಡಿಸು | x ಶೂನ್ಯವಲ್ಲ ಎಂದು ಖಚಿತಪಡಿಸು | पक्का करो | నిర్ధారించు | ❌ |

## 10. Input and output

| Construct | Kannada form | Hindi | Telugu | Today |
|---|---|---|---|---|
| Print | ಮುದ್ರಿಸು / ತೋರಿಸು | छापो | ముద్రించు | ✅ |
| Read input | ಓದು | पढ़ो | చదువు | ✅ command line (switched off in the playground) |
| Files | ಕಡತ ಓದು / ಕಡತ ಬರೆ | फ़ाइल पढ़ो / लिखो | ఫైలు చదువు / రాయి | 🟡 `read-file` / `write-file` have no Kannada words; ಬರೆ is broken (issue 9) |

## 11. Time and concurrency

| Construct | Kannada form | Example | Hindi | Telugu | Today |
|---|---|---|---|---|---|
| Event / callback | **ಯಾವಾಗ … ಆಗ** | ಯಾವಾಗ ಸಂದೇಶ ಬರುತ್ತದೋ ಆಗ … | जब … तब | ఎప్పుడు … అప్పుడు | ❌ |
| Generator | ಒಂದೊಂದಾಗಿ ಕೊಡು | | एक-एक करके दो | ఒక్కొక్కటిగా ఇవ్వు | ❌ |
| Async wait | ಕಾಯು | | रुको / इंतज़ार करो | వేచి ఉండు | ❌ |
| Run in parallel | ಒಟ್ಟಿಗೆ | | एक साथ | ఒకేసారి | ❌ |

## 12. Objects (deferred)

Class (ಮಾದರಿ), method, inheritance and interface. These are left out until
everything above works.

---

## Open issues found while building this table

These were checked against the VM on 2026-11-08.

1. **ತಿರುಗಿಸು is mapped twice** (`src/vocabulary.py:82` rot, `:107` reverse). Python keeps the second entry, so **rot has no Kannada word**: `೧ ೨ ೩ ತಿರುಗಿಸು` fails with `'int' object is not reversible`.
2. **ಸಮ** means both "equal" and "even" (ಸಮ ಸಂಖ್ಯೆ). Proposal: use the case ending to tell them apart. *-ಗೆ ಸಮ* means equals; ಸಮ placed before a noun means even, with ಬೆಸ for odd.
3. **ನಕ್ಷೆ** is the `map` operation, so the dictionary type needs another word. Proposal: **ಕೋಶ**.
4. **ತೆಗೆ** is currently `nth`, but its natural meaning is "remove". Once indexing uses the genitive and ordinal form, ತೆಗೆ is freed up. Reject uses ಹೊರಗಿಡು.
5. **ಆದರೆ** on its own also means "but". The natural form for "if" is the *-ಅರೆ* ending attached to the verb, so the stand-alone ಆದರೆ should be retired eventually.
6. **ಮತ್ತು** is logical *and*, but it also joins nouns (ಐದು ಮತ್ತು ಮೂರು). The grammar has to tell the two apart: joining nouns versus joining conditions.
7. **Range end:** ವ್ಯಾಪ್ತಿ leaves out the end (`೧ ೫ ವ್ಯಾಪ್ತಿ` → `[1, 2, 3, 4]`), but ಒಂದರಿಂದ ಐದರವರೆಗೆ includes 5 in ordinary Kannada. The natural form must include the end.
8. **ಹುಡುಕು vs ಶೋಧಿಸು:** keep ಹುಡುಕು for finding a position in text, and use ಶೋಧಿಸು to search a collection by a condition.
9. **ಬರೆ maps to `write`, which is not a builtin.** `ಓದು` maps to `read` (stdin). The file builtins have no Kannada word.
10. **Telugu:** వడపోత (filter) is a noun, not a command; it should be a verb such as వడపో. అయ్యేవరకు ("until it becomes") is mapped to *while*. మడత (fold) is a noun too.
11. **Hindi:** तबतक ("until then") is mapped to *until*; "… होने तक" would be the natural form.
12. **Reserved but not runnable:** ಇರಲಿ, ಕಾರ್ಯ, ಹಿಂತಿರುಗಿಸು, ಇಲ್ಲದಿದ್ದರೆ, ನಿಲ್ಲಿಸು, ಮುಂದುವರಿಸು, ಪುನರಾವರ್ತಿಸು. These are lexer keywords for the planned structured parser; the VM reports "Unknown word" for them.
13. **Assignment inside a block:** `[ … i := i + ೧ ]` fails with stack underflow. Only the postfix form `i ೧ + i :=` works inside a block.
14. **Words used both as a value and an operation:** ಇಲ್ಲ (False, and part of negation), नहीं (both `not` and False), కాదు (both `not` and False).

## Next steps

1. Review this table: settle the Kannada form for each construct, then Hindi and Telugu.
2. Fix the plain bugs: issues 1, 9 and 13.
3. Write a formal grammar (EBNF) for the case and verb endings this needs: -ಅರೆ, -ಇರುವ ತನಕ, -ಉವವರೆಗೆ, -ಇಂದ…-ವರೆಗೆ, -ಕ್ಕಿಂತ, the genitive with ordinals, the -ಇ participle, and ಎಂದರೆ.
4. Build it one group at a time, adding regression tests in `tests/` for each construct.
