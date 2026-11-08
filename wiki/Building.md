# Building Kapila

## Run the tests

```
python -m pytest -q
```

## Run from source

```
python kapila_gui.py              # desktop editor
python kapila.py myprog.kpl       # interpreter
python kapilac.py myprog.kpl -r   # compile and run
python app.py                     # website, on port 5000
```

## Build the desktop app

This needs PyInstaller.

```
python build_dist.py --gui-only   # just kapila-gui.exe
python build_dist.py              # everything, including the zip
```

`--gui-only` also copies the exe to `static/downloads/`, which is what the website serves.

## Deploy

```
python deploy.py
```

It regenerates the [build status](Build-Status) page, uploads the site and restarts the service.

## Change the logo

Edit `design/kapila-logo.html`, render it to `static/kapila-logo.png`, and write `static/kapila.ico` from that. The exe picks up the icon on its next build.

## Add a wiki page

Add a Markdown file to `wiki/`, list it in `WIKI_PAGES` in `app.py`, and deploy. Link between pages by name, for example `[Roadmap](Compiler-Roadmap)`.
