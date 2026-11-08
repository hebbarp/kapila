# PTP — Proto-Language Protocol

> Status: **draft 0.1, 2026-11-08.** This is a specification for review;
> nothing is implemented yet.
> Related: [`grammar.md`](grammar.md) (the construct map) and
> [`mashables.md`](mashables.md) (the first user of PTP).

## 1. Purpose

Kapila should work in many human languages, and **a program written in one
language should be readable and remixable in any other**, without the reader
knowing the author's language.

Linguists reconstruct a *proto-language*, such as Proto-Dravidian, as the
common ancestor that daughter languages descend from. PTP works the same way:

- Programs are stored in one **proto form** (PF) that belongs to no human language.
- Each human language is a **daughter**: a *language pack* that renders PF into
  its own words and grammar, and parses its own sentences back into PF.
- Anyone can **fork** a pack to build a new language or a dialect.

Kannada (`kn`) is the reference daughter. English (`en`) is a daughter too, with
no special status.

## 2. Terms

| Term | Meaning |
|---|---|
| **Concept** | One unit of meaning the language can express: an operation, a source, a field, a control construct, or a type |
| **Concept ID** | A stable, neutral identifier for a concept, such as `k:0041` |
| **Role** | How an argument relates to an operation (object, instrument, from, to, …). Roles are what case endings, postpositions and prepositions express |
| **Proto form (PF)** | The stored program: a tree of concept IDs, roles, names and literals |
| **Language pack** | The files that define one daughter language |
| **Surface form** | A program as text in one language |
| **Render** | PF → surface form, done by a pack |
| **Parse** | surface form → PF, done by a pack |
| **Registry** | The list of all concepts and roles, with version numbers |

## 3. Concept IDs

- **Neutral and opaque:** `k:` followed by a 4-digit number (`k:0041`). IDs are not words in any language, so no language is the "real" one. This is the same idea as Wikidata's Q-numbers.
- **Stable for ever:** an ID is never reused or given a new meaning. Concepts can be *deprecated*, never deleted.
- **Readable in tools:** the registry stores a short *gloss* per language, and editors and error messages show the gloss in the reader's language, never the bare ID.

Registry entry (`proto/concepts.json`):

```json
{
  "k:0041": {
    "kind": "operation",
    "effect": "( list block -- list )",
    "roles": { "karman": "list", "karana": "block" },
    "meaning": "keep the items for which the block is true",
    "since": "0.1",
    "_note": "the Kapila core stack effect is in 'effect'"
  }
}
```

**All PTP files are JSON**: the registry, the packs and PF documents. That
means one format and one validator (JSON Schema), and both the browser and
Python's standard library can read and write it. JSON has no comments, so any
key beginning with `_` (such as `_note`) is treated as a comment and ignored by
tools.

Glosses come from the packs, so the registry itself contains no human-language
words beyond the developer-facing `meaning` note.

### Concept kinds

| Kind | Examples |
|---|---|
| `operation` | filter, sort, add, print |
| `source` | news, weather, wiki |
| `field` | title, link, latitude |
| `control` | if/else, while, until, for-each, range, define |
| `type` | number, text, list, record |
| `value` | true, false, nothing |
| `question` | an input the program asks for (which, how many) |

## 4. Roles (kārakas)

Arguments are identified by **role**, not by position. Each language then marks
roles its own way: Kannada with case endings, Hindi with postpositions, English
with prepositions and word order. This is what lets one PF render naturally in
languages with very different grammars.

The role names follow Pāṇini's kārakas, which suits Kapila's roots and is not
English:

| Role ID | Meaning | Kannada | English |
|---|---|---|---|
| `kartr` | agent / subject | (unmarked) | subject position |
| `karman` | object | -ಅನ್ನು | object position |
| `karana` | instrument / "by" | -ಇಂದ | by, with |
| `sampradana` | recipient / "to" | -ಗೆ / -ಕ್ಕೆ | to |
| `apadana` | source / "from" | -ಇಂದ | from |
| `adhikarana` | location / "in" | -ಅಲ್ಲಿ | in, on |
| `saha` | accompaniment / "with" | -ಒಂದಿಗೆ | with |
| `avadhi` | limit / "until" | -ವರೆಗೆ | until, up to |
| `tulana` | standard of comparison / "than" | -ಕ್ಕಿಂತ | than |
| `sambandha` | possession / "of" | genitive -ಅ / -ದ / -ಯ | of, 's |

Note that Kannada uses -ಇಂದ for both `karana` and `apadana`. The pack resolves
this from the concept's role list. This is one example of why roles live in the
registry rather than being guessed from the text.

## 5. The proto form (PF)

PF is a JSON tree. It is what gets stored, published, versioned and executed.

Mashable (c) from `mashables.md`, "where is it raining?":

```json
{
  "ptp": "0.1",
  "registry": "0.1",
  "author_lang": "kn",
  "names": {
    "n:1": { "kn": "ಮಳೆ-ನಕ್ಷೆ", "en": "rain-map" }
  },
  "body": [
    { "c": "k:0102", "_gloss": "show-on-map",
      "karman": {
        "c": "k:0041", "_gloss": "filter",
        "karman": {
          "c": "k:0050", "_gloss": "transform-each",
          "karman": { "list": [
            { "text": "ಬೆಂಗಳೂರು", "lang": "kn" },
            { "text": "ಮೈಸೂರು", "lang": "kn" },
            { "text": "ಮಂಗಳೂರು", "lang": "kn" },
            { "text": "ಹುಬ್ಬಳ್ಳಿ", "lang": "kn" }
          ] },
          "karana": { "c": "k:0201", "_gloss": "weather" }
        },
        "karana": {
          "c": "k:0010", "_gloss": "greater-than",
          "karman": { "field": "k:0310", "_gloss": "rain" },
          "tulana": { "num": 0 }
        }
      }
    }
  ]
}
```

(`_gloss` keys are for people reading this document; real PF omits them.)

- **Execution:** PF compiles to the existing postfix Kapila core. The VM's builtin table is keyed by concept ID.
- **Canonical:** two programs mean the same thing exactly when their PF is identical after normalization (sorted keys, fixed literal formats).

## 6. Things that are not concepts

Concepts translate deterministically. Three kinds of content do not, and PTP
handles each differently.

### 6.1 Names people choose (variables, words, mashable names)
- Each name is an entry in the PF `names` table with a **label per language**.
- The **author** gives the label in their language. **Anyone** can add a label in another language, wiki-style. Labels are part of the published version.
- If the reader's language has no label, show a **deterministic transliteration** of the author's label into the reader's script, marked as a transliteration. **Pampa** (`D:/pampa`) is the transliteration engine; see §6.4.
- Labels never change what the program does: names are matched by ID, not by text.

### 6.2 Quoted text (literals)
- Literals are **values**, and **they are never translated during execution**. `"ಮಳೆ"` used as a search word must stay `"ಮಳೆ"`, or the program's behaviour would change.
- For display, a literal may carry a **gloss** in other languages, added by a person. A machine gloss is allowed only when it is clearly marked as one.
- Every literal records its language (`"lang": "kn"`).

### 6.3 Data (headlines, summaries, place names from sources)
- Shown as it arrives, with its language tagged.
- An optional **translate** concept may convert data using machine translation. Its output is always labelled as machine-translated, and the original stays available.

### 6.4 Transliteration with Pampa

**Decided (2026-11-08):** PTP uses Pampa for transliteration. Pampa already
defines 12 Indic scripts, splits text into aksharas and detects scripts, but it
has no transliteration yet. Building it there means Pampa gains a feature that
is useful beyond Kapila.

What Pampa needs:

1. **Between Brahmic scripts** (Kannada ↔ Telugu ↔ Devanagari ↔ …). Pampa's own
   observation is that these Unicode blocks share the same layout, so most
   letters convert by a fixed code-point offset. Exception tables cover the
   rest: letters one script lacks, such as Tamil's missing aspirates and voiced
   consonants, and Kannada/Telugu ಳ/ಱ; short e/o; nukta; and script-specific
   signs.
2. **Brahmic → Latin**, using **ISO 15919**, so English readers see Kannada
   names romanized (ಊರು → *ūru*). This is deterministic and reversible.
3. **Latin → Brahmic only for ISO 15919 input.** Ordinary English spelling isn't
   phonetic ("town" can't be transliterated reliably), so English names without
   a Kannada label are shown in Latin script, marked as untranslated.
4. **Work by akshara, not by code point**, using Pampa's segmenter, so conjuncts
   and vowel signs come out correctly.
5. **A shared test set** of names and words with expected output, checked in
   both directions where a mapping is reversible.

## 7. Language packs

A pack is a folder, `langs/<code>/`, for example `langs/kn/` and `langs/en/`.

| File | Contents |
|---|---|
| `pack.json` | name, script, writing direction, digits, word order, registry version supported, `forked_from` |
| `lexicon.json` | concept ID → surface words: one **canonical** form for rendering, plus accepted **aliases** for parsing |
| `morphology.json` | how each role is marked (suffix, postposition, preposition, or word order); verb forms (conditional, participle chain, relative clause, until-form); genitive; ordinals; number words |
| `grammar.json` | sentence-layer rules: how constructs are arranged into sentences, for both parsing and rendering |
| `ui.json` | interface text, including the playground, mashables and sign-in screens |
| `tests/` | pack-specific test cases, in addition to the shared conformance set |

### How a concept can be expressed

| Expression | Example |
|---|---|
| `word` | ಸೋಸು → `k:0041` (filter) |
| `suffix` | -ಇಂದ marks `apadana` (Kannada) |
| `postposition` | से marks `apadana` (Hindi) |
| `preposition` | *from* marks `apadana` (English) |
| `order` | the object comes right after the verb (English) |
| `particle` | a separate small word (e.g. a question marker) |

### Lexicon entry examples

```json
// langs/kn/lexicon.json
{ "k:0041": { "canonical": "ಸೋಸು", "aliases": [], "gloss": "ಹೊಂದುವವನ್ನು ಉಳಿಸು", "_note": "filter" } }

// langs/en/lexicon.json
{ "k:0041": { "canonical": "filter", "aliases": ["keep"], "gloss": "keep the items that match" } }
```
(The `//` lines only label the two files here; they are not part of the JSON.)

### Ambiguity
A surface form may map to more than one concept **only** if the pack gives a
rule that decides between them. Example: ಸಮ means "equals" when it follows a
noun in the dative (-ಗೆ ಸಮ), and "even" when it comes before a noun (ಸಮ ಸಂಖ್ಯೆ).
The conformance checker reports any ambiguity that has no rule.

## 8. Render and parse

- **Round trip (required):** `parse(render(pf)) == pf` for every PF in the conformance set.
- **Normalization (allowed):** `render(parse(text))` may differ from what the author typed. For example, aliases become canonical words and spacing is standardized. The author sees the normalized text.
- **Parse errors are in the writer's language**, and point to the word that couldn't be understood.
- **Never guess.** If a sentence has two possible readings and no rule decides, it is an error that lists the readings. It is never silently resolved.

## 9. Conformance

Shared test set: `proto/tests/*.pf.json`, PF documents covering every concept.

| Level | Meaning |
|---|---|
| **L0 — Words** | every covered concept has a canonical word; postfix programs round-trip |
| **L1 — Sentences** | the sentence layer round-trips the core constructs: the participle chain, roles, if/else, loops, questions |
| **L2 — Full** | every concept in the registry, with every test passing |

Every pack publishes a **coverage report**: its level, which concepts it covers,
and which tests fail. A partial pack is fine; it's labelled as partial, and
programs using uncovered concepts fall back to showing the concept's gloss from
the nearest pack (by default the author's language).

## 10. Versions

- The **registry** is versioned with semantic versions. Adding concepts is a minor version; deprecating is a minor version; there are no removals.
- Each **PF document** records the registry version it was written against.
- Each **pack** declares which registry version it supports.
- A **published mashable** is pinned to its versions, so later changes to a pack can't change what an existing program does.

## 11. Forking

- A pack is forked like any repository. `pack.json` records `forked_from`, so lineage stays visible.
- A **dialect** (for example a regional Kannada) is a fork that overrides only some entries.
- A **registry of packs** comes later: it lists packs, maintainers, coverage level and lineage.
- **New concepts** are proposed against the registry, not added by packs on their own, so every language stays mutually understandable.

## 12. What the reader experiences

When someone opens a mashable:
1. It is rendered in **the reader's language**, with concepts shown in their own words and grammar.
2. **Names** appear in the reader's language if a label exists; otherwise they are transliterated, with a marker.
3. **Quoted text and data** appear as they are, with a gloss when one exists.
4. A small note shows the **author's language**, and a "view original" switch shows the author's own text.

## 13. Moving the current code to PTP

1. **Build the registry** from the builtins (`src/vm/builtins.py`) and the rows of `grammar.md`.
2. **Key the VM's builtin table by concept ID**, instead of by English name.
3. **Move the vocabulary into packs:** the Kannada words from `src/vocabulary.py` and `src/lexer/keywords.py` go to `langs/kn/`, the English names to `langs/en/`. The Hindi and Telugu words move to `langs/hi/` and `langs/te/`, unlisted until they reach L0.
4. **Store mashables as PF** from the start.
5. **Turn the language toggle back on** in the playground (hidden 2026-11-08) once the `kn` and `en` packs exist; other languages appear as their packs reach L0.
6. **Fix the existing word clashes** recorded in `grammar.md` (ತಿರುಗಿಸು, ಸಮ, ನಕ್ಷೆ, ತೆಗೆ) as part of writing the Kannada pack, since the checker will reject them.

## 14. Open questions

1. ~~**Registry format.**~~ **Decided: JSON** for everything, with `_`-prefixed keys as comments (§3).
2. ~~**Concept numbering.**~~ **Decided: one flat sequence** (`k:0001`, `k:0002`, …). IDs say nothing about category; the registry's `kind` field does that.
3. **Who approves new concepts** once outside packs exist?
4. ~~**Transliteration rules.**~~ **Decided: Pampa** is the transliteration engine (§6.4).
5. **PF size and diffs:** JSON trees are verbose. Do we also need a compact text form of PF for diffs and debugging?
