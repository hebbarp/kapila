# Development log

Newest first.

## 8 November 2026

**Compiler**

- Verb-last assignment compiles correctly. `ಅ := ೨ ೩ ಕೂಡು.` used to give 2 and now gives 5.
- The compiler stops with a line number on anything it can't build, instead of skipping it.
- Writing `ಅ = ೫` on an unknown name now suggests `:=`, in both the compiler and the interpreter.

**Desktop**

- The desktop app became an editor in the style of DrRacket: definitions above, interactions below, with Run, Stop, syntax colouring, bracket matching and open and save.
- It has its own Kapila logo.
- It is downloadable from the home page.

**Website**

- New home page with the playground in the hero. The full playground moved to `/play`.
- First-visit welcome and a link preview card.
- This wiki.

**Language**

- Records, with Kannada field names and genitive access such as `ಹವಾಮಾನದ ಸ್ಥಿತಿ`.
- Live sources: news in eight sections, weather and Wikipedia.
- A step trace in the playground showing every word run and every request sent.
- Design documents for the grammar, mashables and the proto-language protocol.

**Other**

- The natural-language tab is hidden, and the engine is kept for internal use.
- The language toggle is hidden until language packs exist.

## 25 February 2026

- Sandarbha context-aware mode added to the playground.

## 17 January 2026

- The desktop REPL captures printed output.

## 16 January 2026

- First commit of Kapila.
- Runtime library for compiled programs.
- Standalone Windows distribution with TinyCC bundled, released as v0.6.0.
