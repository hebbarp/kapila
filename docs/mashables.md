# Mashables — Yahoo Pipes, in Kannada

> Status: **design draft, 2026-11-08.** Nothing here is built yet. All the
> Kannada forms are proposals and need review by a native speaker.
> Related: [`grammar.md`](grammar.md) (the construct-by-construct grammar map).

## 1. The idea

Around 2007, Yahoo Pipes let anyone combine feeds, listings and search results
into something new in an afternoon. A published pipe could then become an
input to someone else's pipe, and the whole community built on itself.

**Mashables brings that back with Kannada as the medium.** There is no visual
editor and no boxes and wires: **the sentence is the pipe.** Kannada grammar
already has a form for everything Pipes had to draw:

| Pipes drew… | Kannada already has… |
|---|---|
| source boxes | **nouns** (ಸುದ್ದಿ news, ಹವಾಮಾನ weather, ವಿಕಿ Wikipedia) |
| operator boxes | **verbs** (ಸೋಸು filter, ವಿಂಗಡಿಸು sort, ಎಣಿಸು count) |
| wires | the **-ಇ verb chain** ("having fetched…, having filtered…, show") |
| filter conditions | **descriptive clauses** (ಮಳೆ ಇರುವ ಊರುಗಳು "the towns where it is raining") |
| join two sources | the **sociative ending -ಒಂದಿಗೆ** ("with") |
| group by | **-ಅನುಸಾರ** ("according to") |
| user input boxes | **question words** (ಯಾವ ಊರು? "which town?") |
| output module | the **final verb** (ತೋರಿಸು show) |

## 2. Principles

1. **Text only.** You edit text. The *results* can appear as a list, table, card or map.
2. **Everything is a list of records.** Every source returns records with shared field names, so any source can be filtered, sorted, joined or mapped like any other.
3. **A published mashable is a new word.** Others call it like any built-in word. That is how the vocabulary grows, which is how Forth grows too.
4. **Kannada and English only for now.** Kannada is primary, with English aliases so people who don't speak Kannada can still read and remix mashables. Other languages join later as forks under the PTP language protocol (`ptp.md`).
5. **Same sentence, same program.** The sentence is parsed by a fixed grammar, with no guessing.

## 3. Anatomy of a mashable

```
[questions]  →  source(s)  →  verbs chained with -ಇ  →  final verb (output)
```

```
ಯಾವ ಊರು?                                     ← input: "which town?"
ಊರಿನ ಹವಾಮಾನ ತಂದು,                             ← source: "having fetched the town's weather,"
ಊರಿನ ಸುದ್ದಿಯಲ್ಲಿ ಮೊದಲ ಐದನ್ನು ಅದರೊಂದಿಗೆ ತೋರಿಸು.     ← output: "show the first five of the town's news with it."
```

The sentence layer **lowers** to ordinary postfix Kapila. The lowered form
uses English builtin names here for clarity:

```
"ಊರು" ask  weather  "ಊರು" @ news 5 take  combine show
```

## 4. Records

A record is a map from field names to values. The **standard fields** are
shared across sources so they can be mixed:

| Field | Meaning | English alias |
|---|---|---|
| ಶೀರ್ಷಿಕೆ | title / headline | title |
| ಸಾರಾಂಶ | summary | summary |
| ಕೊಂಡಿ | link (URL) | link |
| ಮೂಲ | source / publisher | source |
| ಸಮಯ | time (ISO 8601) | time |
| ಸ್ಥಳ | place name | place |
| ಅಕ್ಷಾಂಶ / ರೇಖಾಂಶ | latitude / longitude | lat / lon |
| ಚಿತ್ರ | image URL | image |

Rules:
- **Field access uses the genitive.** ಸುದ್ದಿಯ ಶೀರ್ಷಿಕೆ means "the news's title". On a list of records it returns that field from every record.
- **Any record with ಅಕ್ಷಾಂಶ and ರೇಖಾಂಶ can be put on a map.** This is what made the original mashups impressive.
- Postfix building blocks: ಪಡೆ (get field), ಇಡು (set field), ಕೀಲಿಗಳು (keys), and the existing `{ key: value }` literal.

## 5. Sources (first three)

Each source is a noun that **fetches** (ತರು) a list of records. None of these
need an API key.

| Noun | Alias | Gives | Provider | Notes |
|---|---|---|---|---|
| **ಸುದ್ದಿ** | news | headlines: ಶೀರ್ಷಿಕೆ ಮೂಲ ಕೊಂಡಿ ಸಮಯ (newest first, at most 20) | **Kannada topic or empty:** the RSS feeds of ಪ್ರಜಾವಾಣಿ, ಒನ್‌ಇಂಡಿಯಾ ಕನ್ನಡ, ಟಿವಿ9 ಕನ್ನಡ and ಕನ್ನಡಪ್ರಭ, combined and searched by title. **Otherwise:** Google News, English (India) edition | Google News's "Kannada edition" serves Hindi (checked 2026-11-08), so it isn't used. A Kannada topic also matches inflected forms (ಬೆಂಗಳೂರು matches ಬೆಂಗಳೂರಿನಲ್ಲಿ) |
| **ಹವಾಮಾನ** | weather | one record: ಸ್ಥಳ ತಾಪಮಾನ (°C) ಮಳೆ (mm) ಗಾಳಿ (km/h) ಸ್ಥಿತಿ ಅಕ್ಷಾಂಶ ರೇಖಾಂಶ | Open-Meteo (place lookup + forecast); OpenStreetMap Nominatim when Open-Meteo doesn't know the place (e.g. ಹುಬ್ಬಳ್ಳಿ) | ಸ್ಥಿತಿ ("condition") is a Kannada description of the weather code |
| **ವಿಕಿ** | wiki | one record: ಶೀರ್ಷಿಕೆ ಸಾರಾಂಶ ಕೊಂಡಿ ಚಿತ್ರ (+ ಅಕ್ಷಾಂಶ ರೇಖಾಂಶ if the article has them) | Wikipedia REST summary | kn.wikipedia for a Kannada title, en.wikipedia otherwise |

**News sections** (added 2026-11-08). A topic that names a section reads that
section's own feeds instead of searching headlines, and each record gets a
ವಿಭಾಗ (section) field:

| Section | Kannada names | English names | Kannada feeds | English |
|---|---|---|---|---|
| ವಾಣಿಜ್ಯ business | ವಾಣಿಜ್ಯ ಉದ್ಯಮ ವ್ಯಾಪಾರ ವ್ಯವಹಾರ | business | TV9, Kannada Prabha | Google News topic |
| ಕ್ರೀಡೆ sports | ಕ್ರೀಡೆ ಕ್ರೀಡಾ | sports, sport | TV9, Kannada Prabha | Google News topic |
| ಸಿನಿಮಾ cinema | ಸಿನಿಮಾ ಚಲನಚಿತ್ರ ಮನರಂಜನೆ | cinema, movies, entertainment | TV9, Kannada Prabha, OneIndia | Google News topic |
| ತಂತ್ರಜ್ಞಾನ technology | ತಂತ್ರಜ್ಞಾನ ಟೆಕ್ | technology, tech | TV9 | Google News topic |
| ರಾಜಕೀಯ politics | ರಾಜಕೀಯ | politics | TV9, Kannada Prabha | Google News search |
| ರಾಜ್ಯ Karnataka | ರಾಜ್ಯ ಕರ್ನಾಟಕ | karnataka, state | TV9, Kannada Prabha | Google News search |
| ದೇಶ national | ದೇಶ ರಾಷ್ಟ್ರೀಯ ಭಾರತ | india, national, nation | TV9, Kannada Prabha | Google News topic |
| ವಿಶ್ವ world | ವಿಶ್ವ ಜಗತ್ತು ಅಂತಾರಾಷ್ಟ್ರೀಯ ವಿದೇಶ | world, international | TV9, Kannada Prabha | Google News topic |

How the feeds were chosen: each publisher's section feed was compared with its
main feed. TV9's `cinema`, `state` and `india` addresses just repeat the main
feed, so they aren't used (TV9's `entertainment`, `karnataka` and `national` are).
Prajavani's section feeds carry only 1–2 items, so Prajavani is used for
headline search only.

Later candidates: Mastodon/Bluesky (social), Hacker News, OpenStreetMap places,
data.gov.in, YouTube, GitHub. Each new source must return the standard fields
wherever they apply.

## 6. Verbs (operators)

| Verb | Alias | Pipes module | Example meaning | Today |
|---|---|---|---|---|
| ಸೋಸು | filter | Filter (keep) | keep the ones where it is raining | ✅ word exists |
| ಹೊರಗಿಡು | reject | Filter (remove) | leave out the sports news | ❌ |
| ವಿಂಗಡಿಸು / ಅನುಸಾರ | sort / sort-by | Sort | sort by a field: `"ಸಮಯ" ಅನುಸಾರ` ("according to time"); add ತಿರುಗಿಸು for newest first | ✅ |
| ಮೊದಲ *N* | take | Truncate | the first five | ✅ ತೆಗೆದುಕೊ |
| ಕೊನೆಯ *N* | last | Tail | the last three | ❌ |
| ಸೇರಿಸು | union | Union | news *and* wiki, together | 🟡 append |
| ಹೊಂದಿಸು | join | (Loop + Sub-element) | match news with weather by place | ❌ |
| ಎಣಿಸು | count | Count | how many | ❌ (ಉದ್ದ length exists) |
| ಗುಂಪಿಸು | group | (none) | group by source (ಮೂಲದ ಅನುಸಾರ) | ❌ |
| ಹೆಸರಿಸು | rename | Rename | call the title "headline" | ❌ |
| ಒಂದೊಂದೇ ಇರಿಸು | unique | Unique | keep one of each | ❌ (wording TBD) |
| ಪ್ರತಿಯೊಂದನ್ನೂ … | map | Loop | for each one, fetch its wiki | ✅ map (wording: see §10) |

## 7. Inputs: question words

A question in the sentence **declares an input**:

| Question | Meaning | Input kind |
|---|---|---|
| ಯಾವ ಊರು? | which town? | text, named ಊರು |
| ಎಷ್ಟು ಸುದ್ದಿ? | how many news items? | number |
| ಯಾವ ವಿಷಯ? (ಕ್ರಿಕೆಟ್) | which topic? (default: cricket) | text with a default |

- On a **published page**, each question becomes an input box, with the question itself as the label.
- When **another mashable calls it as a word**, the answers come from the stack in the order the questions appear.
- Later, the noun used in the answer is available by name, as ಊರಿನ ("the town's").

## 8. Output: the final verb

| Verb | Shows as |
|---|---|
| ತೋರಿಸು (show) | chosen automatically: a **map** if the records have ಅಕ್ಷಾಂಶ/ರೇಖಾಂಶ, a **card** for a single record, a **list** if they have ಶೀರ್ಷಿಕೆ, otherwise a **table** |
| ಪಟ್ಟಿಮಾಡು (list) | a list of headlines with links |
| ಕೋಷ್ಟಕದಲ್ಲಿ ತೋರಿಸು (show in a table) | a table |
| ನಕ್ಷೆಯಲ್ಲಿ ತೋರಿಸು (show on a map) | a map |
| ಹೇಳು (say) | spoken aloud (later) |

Every published mashable is also available as **`.json`** and **`.rss`**, so
outside tools, and other mashables, can consume it.

## 9. Publishing and remixing

- **Defining** uses the grammar's definition form: *X ಎಂದರೆ …* ("X means …").
- **Publishing** gives the mashable a page, `.json` and `.rss` links, and a word name that others can call, for example ಊರಿನ-ವರದಿ ("town report").
- **Remixing** copies the text into your editor. The page shows "remixed from …", so the lineage stays visible.
- **Versions** are fixed once published. A mashable that uses another one is pinned to the version it was built against, so an author's later edits can't break other people's mashables.
- A **gallery** lists the newest, most-remixed and most-used mashables.

## 10. Three examples

**a) Town report** (inputs plus two sources)
```
ಯಾವ ಊರು?
ಊರಿನ ಹವಾಮಾನ ತಂದು, ಊರಿನ ಸುದ್ದಿಯಲ್ಲಿ ಮೊದಲ ಐದನ್ನು ಅದರೊಂದಿಗೆ ತೋರಿಸು.
```
*Which town? Fetch the town's weather, and show it with the first five news items about the town.*

**b) Topic explainer** (Wikipedia plus news)
```
ಯಾವ ವಿಷಯ?
ವಿಷಯದ ವಿಕಿ ಸಾರಾಂಶ ಮತ್ತು ಇತ್ತೀಚಿನ ಹತ್ತು ಸುದ್ದಿ ತಂದು ತೋರಿಸು.
```
*Which topic? Fetch the topic's Wikipedia summary and the ten latest news items, and show them.*

**c) Where is it raining?** (map over a list, filter, map view)
```
ಬೆಂಗಳೂರು, ಮೈಸೂರು, ಮಂಗಳೂರು, ಹುಬ್ಬಳ್ಳಿ —
ಪ್ರತಿಯೊಂದರ ಹವಾಮಾನ ತಂದು, ಮಳೆ ಇರುವವನ್ನು ಸೋಸಿ, ನಕ್ಷೆಯಲ್ಲಿ ತೋರಿಸು.
```
*For each of these cities, fetch the weather, keep the ones where it is raining, and show them on a map.*

Lowered to postfix Kapila (English builtin names):
```
[ "ಬೆಂಗಳೂರು" "ಮೈಸೂರು" "ಮಂಗಳೂರು" "ಹುಬ್ಬಳ್ಳಿ" ] [ weather ] map
[ "ಮಳೆ" get 0 > ] filter
map-show
```

## 11. How it gets built: two layers

1. **Core (postfix Kapila):** records, the source words, the verbs and the output views. These are usable straight away in postfix form, as in the lowered examples above.
2. **Sentence layer:** a parser for the fixed grammar (the -ಇ chain, genitive, sociative, descriptive clauses and question words) that lowers sentences into the core. This is the grammar work from `grammar.md`, driven by real use.

Building the core first means each source and verb is testable on its own, and
the sentence layer then has something concrete to target.

## 12. Safety

- **Fixed sources only**: no arbitrary URL fetch at first, so the server can't be used to probe or relay requests.
- **Limits per run**: at most about 5 fetches, 8-second timeouts, a cap on records per source, and 10-minute caching per query.
- **Per-IP rate limits** on runs. Published mashables run under the same limits.
- **Everything from a feed is escaped** before display; titles and summaries are treated as text, never HTML.
- **API keys stay on the server** and are never shown in mashables or their output.

## 13. Open decisions

1. ~~**Accounts for publishing.**~~ **Decided (2026-11-08): Kapila gets its own authentication, separate from SpaceD**, in Kannada, using a name and passphrase (see §15).
2. **ನಕ್ಷೆ clash.** ನಕ್ಷೆ is currently the higher-order `map` builtin, but in mashables it naturally means a geographic map (ನಕ್ಷೆಯಲ್ಲಿ ತೋರಿಸು). Proposal: keep ನಕ್ಷೆ for geographic maps, and express "transform each" with the natural ಪ್ರತಿಯೊಂದನ್ನೂ … form.
3. **Verb wording** for unique, join and rename (§6).
4. **Word names for published mashables**: one global name per mashable, or prefixed by author?
5. **News edition**: should the language of the topic choose the edition, or should there be an explicit choice?

## 14. Build order

1. ✅ Records: ಪಡೆ/ಇಡು/ಕೀಲಿಗಳು/ಮೌಲ್ಯಗಳು, genitive field access, sort-by-field (ಅನುಸಾರ). Built 2026-11-08 (`src/vm/records.py`, `tests/test_records.py`).
2. ✅ The three sources, with the safety limits, plus tests run against recorded responses. Built 2026-11-08 (`src/vm/sources.py`, `tests/test_sources.py`). Assignment now takes a postfix result (`x := "ಮಳೆ" ಸುದ್ದಿ.`), on the same line as `:=`.
3. Output views (list, card, table, map) in the playground, plus `.json` output.
4. Questions as inputs.
5. Kapila accounts (§15), then publish, the gallery and remix.
6. The sentence layer, starting with the -ಇ chain, the genitive and question words.

## 15. Kapila accounts

Kapila has its own accounts, separate from SpaceD.

- **What needs an account:** publishing, remixing into your own name, and higher run limits. **Running and reading mashables stays anonymous**, so anyone can try one from a shared link.
- **Storage:** SQLite on the Kapila server (`users`, `sessions`, `mashables`, `versions`).
- **Sessions:** a signed, HttpOnly, Secure, SameSite=Lax cookie. Accounts are identified by a random user ID; the display name is changeable and used as the author prefix.
- **Safety:** rate-limited sign-in attempts, CSRF protection on every write, no third-party trackers.
- **Kannada throughout:** every screen, label, button, error message and outgoing message (email or WhatsApp) is in Kannada first, with English alongside. Other languages come later through PTP (`ptp.md`). Examples: ಒಳಗೆ ಬನ್ನಿ ("sign in"), ಹೊಸ ಖಾತೆ ("new account"), ಹೊರಗೆ ಹೋಗಿ ("sign out").
- **Kannada names:** display names and author prefixes may be in Kannada script. Names are normalized to Unicode NFC, limited to one script per name (no mixing Kannada and Latin), and stripped of invisible characters other than the ZWJ/ZWNJ that Kannada needs. This stops two names that look identical from being different accounts.
- **Kannada passphrases:** if passwords are used, they are normalized to NFC before hashing, so the same Kannada passphrase typed on different keyboards still matches.
- **Login method — decided (2026-11-08): name + passphrase.** The passphrase may be in Kannada. It is NFC-normalized and hashed with scrypt (from Python's standard library), with a per-user salt. Minimum length is counted in characters, not bytes. No outside service is needed.
- **Recovery:** passphrases can't be recovered by email or phone yet. At sign-up the user is shown a one-time **recovery code** (ಮರುಪಡೆಯುವ ಸಂಕೇತ, "recovery code") to keep safe. An email or WhatsApp recovery option can be added later.
