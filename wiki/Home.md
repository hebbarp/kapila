# ಕಪಿಲ wiki

This wiki tracks how Kapila is being built: where the compiler is heading, what works today, and what changed. The pages live in the `wiki/` folder of the repository, and each deploy publishes them here.

| Page | What it answers |
|---|---|
| [Compiler roadmap](Compiler-Roadmap) | Why Kapila compiles through C first, and how LLVM comes in later |
| [Build status](Build-Status) | Which programs run, compile and agree today. Regenerated on every deploy |
| [Development log](Development-Log) | What changed, by date |
| [Building Kapila](Building) | How to run the tests, build the desktop app and deploy |

## What Kapila is made of

- **Interpreter.** A stack machine in Python. It powers the playground and the desktop editor, and it is where new language features arrive first.
- **Compiler.** `kapilac` turns the same programs into native executables by way of C.
- **Desktop editor.** A definitions window above an interactions window, in the style of DrRacket.
- **Language packs.** Planned. See the protocol work under way in `docs/ptp.md`.
