#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ಕಪಿಲ (Kapila) desktop editor.

Laid out the way DrRacket is: a definitions window above an interactions
window. Run starts a fresh interpreter, evaluates the definitions, and leaves
you at a prompt where everything they defined is still available.
"""

import bisect
import ctypes
import os
import queue
import re
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from tkinter import font as tkfont

kapila_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, kapila_dir)

from src import __version__
from src.vm import VM
from src.vocabulary import VOCABULARY

INDIGO = '#1E2463'
KUMKUM = '#B81D2A'
PAPER = '#FFFFFF'
PANEL = '#EEF0F7'
LINE = '#D3D7E6'
SOFT = '#6A6F92'

PROMPT = 'ಕಪಿಲ> '
FILE_TYPES = [('ಕಪಿಲ programs', '*.kpl'), ('All files', '*.*')]
HIGHLIGHT_LIMIT = 200_000     # characters; beyond this, skip colouring
REPL_MAX_LINES = 6000
POLL_BATCH = 300              # events taken from a running program per UI tick

STARTER = '''// ಇಲ್ಲಿ ಪ್ರೋಗ್ರಾಮ್ ಬರೆದು ಓಡಿಸು ಒತ್ತಿ (F5).
// Write your program here and press Run (F5).

ವರ್ಗ: ನಕಲು ಗುಣಿಸು ॥

ಅ := ೧೨ ವರ್ಗ.
ಅ ಮುದ್ರಿಸು.
'''

TOKEN_RE = re.compile(r'//[^\n]*|/\*.*?(?:\*/|\Z)|"[^"\n]*"?|:=|[^\s\[\]{}()"]+', re.DOTALL)
NUMBER_RE = re.compile(r'-?[0-9೦-೯]+(?:\.[0-9೦-೯]+)?$')
OPENERS = {'[': ']', '{': '}', '(': ')'}
CLOSERS = {v: k for k, v in OPENERS.items()}
SYNTAX_TAGS = ('comment', 'string', 'number', 'keyword', 'defn', 'bracket_match')


def to_kannada(value):
    """Convert value to Kannada representation."""
    if isinstance(value, bool):
        return 'ಸರಿ' if value else 'ತಪ್ಪು'
    if isinstance(value, (int, float)):
        kannada_digits = '೦೧೨೩೪೫೬೭೮೯'
        return ''.join(kannada_digits[int(ch)] if ch.isdigit() else ch for ch in str(value))
    if isinstance(value, list):
        items = ' '.join(to_kannada(x) for x in value)
        return f'[ {items} ]'
    return str(value)


class _Stopped(BaseException):
    """Raised inside the worker thread by the Stop button. Not an Exception,
    so nothing in the interpreter can swallow it."""


class _Writer:
    """stdout for the program: hands text to the UI as it is printed."""

    def __init__(self, events):
        self.events = events

    def write(self, text):
        # Only the program's own thread may wait on the queue. The UI thread
        # drains it, so a stray traceback there must never block.
        if text and threading.current_thread() is not threading.main_thread():
            self.events.put(('out', text))
        return len(text)

    def flush(self):
        pass


class _Reader:
    """stdin for the program: asks the UI for a line."""

    def __init__(self, app):
        self.app = app

    def readline(self):
        self.app.events.put(('input',))
        return self.app.answers.get() + '\n'


def _error_line(vm, error):
    """Best guess at the source line an error came from, or None."""
    line = getattr(error, 'line', None)
    if line:
        return line
    tokens = getattr(vm, 'tokens', None)
    if tokens:
        token = tokens[max(min(vm.pos - 1, len(tokens) - 1), 0)]
        return token.line or None
    return None


class KapilaGUI:
    def __init__(self, root, path=None):
        self.root = root
        self.path = None
        self.saved_text = STARTER
        self.vm = VM()
        self.busy = False
        self.worker = None
        self.events = queue.Queue(maxsize=1000)  # a print loop waits for the UI
        self.answers = queue.Queue()
        self.history = []
        self.history_idx = 0
        self._highlight_job = None

        root.geometry('1040x740')
        root.configure(bg=PANEL)
        try:
            # default= also covers dialogs; _MEIPASS is the unpacked exe.
            base = getattr(sys, '_MEIPASS', kapila_dir)
            root.iconbitmap(default=os.path.join(base, 'static', 'kapila.ico'))
        except tk.TclError:
            pass  # no icon is better than no editor
        root.protocol('WM_DELETE_WINDOW', self.quit)

        family = 'Segoe UI'
        for f in ('Noto Sans Kannada', 'Nirmala UI', 'Tunga', 'Arial Unicode MS'):
            if f in tkfont.families():
                family = f
                break
        self.font = (family, 13)
        self.bold = (family, 13, 'bold')
        self.small = (family, 10)

        self._build_toolbar()
        self._build_panes()
        self._build_status()
        self._build_menu()
        self._bind_keys()

        self._reset_repl()
        self._new_prompt()
        self._set_editor_text(STARTER)
        if path:
            self._load(path)
        self.editor.focus_set()
        self._on_cursor()

    # === Layout ===

    def _build_toolbar(self):
        bar = tk.Frame(self.root, bg=PANEL)
        bar.pack(fill=tk.X, padx=10, pady=(8, 6))

        self.name_label = tk.Label(bar, font=self.bold, bg=PANEL, fg=INDIGO)
        self.name_label.pack(side=tk.LEFT)

        button = {'font': self.font, 'relief': tk.FLAT, 'padx': 14, 'pady': 2,
                  'cursor': 'hand2', 'bd': 0}
        self.stop_button = tk.Button(bar, text='■ ನಿಲ್ಲಿಸು', command=self.stop, state=tk.DISABLED,
                                     bg='#FFFFFF', fg=KUMKUM, **button)
        self.stop_button.pack(side=tk.RIGHT, padx=(6, 0))
        self.run_button = tk.Button(bar, text='▶ ಓಡಿಸು', command=self.run_program,
                                    bg=KUMKUM, fg='#FFFFFF', activebackground='#9E1722',
                                    activeforeground='#FFFFFF', **button)
        self.run_button.pack(side=tk.RIGHT, padx=(6, 0))
        self.save_button = tk.Button(bar, text='ಉಳಿಸು', command=self.save, state=tk.DISABLED,
                                     bg='#FFFFFF', fg=INDIGO, **button)
        self.save_button.pack(side=tk.RIGHT)

    def _build_panes(self):
        panes = tk.PanedWindow(self.root, orient=tk.VERTICAL, sashwidth=7, sashrelief=tk.FLAT,
                               bg=LINE, bd=0)
        panes.pack(fill=tk.BOTH, expand=True, padx=10)

        top = tk.Frame(panes, bg=PAPER)
        self.gutter = tk.Canvas(top, width=44, bg=PANEL, highlightthickness=0)
        self.gutter.pack(side=tk.LEFT, fill=tk.Y)
        scroll = tk.Scrollbar(top, command=self.editor_yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.editor = tk.Text(top, font=self.font, bg=PAPER, fg='#1A1D3F', insertbackground=INDIGO,
                              relief=tk.FLAT, bd=0, padx=10, pady=8, wrap=tk.WORD, undo=True,
                              maxundo=-1, tabs=('40p',), spacing1=2, spacing3=2,
                              yscrollcommand=lambda a, b: (scroll.set(a, b), self._draw_gutter()))
        self.editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.editor.tag_configure('errline', background='#FFD9D9')
        self.editor.tag_configure('comment', foreground='#7A7F9C')
        self.editor.tag_configure('string', foreground='#1F7A4D')
        self.editor.tag_configure('number', foreground=KUMKUM)
        self.editor.tag_configure('keyword', foreground=INDIGO, font=self.bold)
        self.editor.tag_configure('defn', foreground='#8A4B00', font=self.bold)
        self.editor.tag_configure('bracket_match', background='#D9DEF2')

        bottom = tk.Frame(panes, bg=PAPER)
        repl_scroll = tk.Scrollbar(bottom)
        repl_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.repl = tk.Text(bottom, font=self.font, bg='#FBFBFE', fg='#1A1D3F',
                            insertbackground=INDIGO, relief=tk.FLAT, bd=0, padx=10, pady=8,
                            wrap=tk.WORD, spacing1=2, spacing3=2,
                            yscrollcommand=repl_scroll.set)
        repl_scroll.config(command=self.repl.yview)
        self.repl.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.repl.tag_configure('banner', foreground=SOFT)
        self.repl.tag_configure('prompt', foreground='#B8860B')
        self.repl.tag_configure('out', foreground='#5B2A86')
        self.repl.tag_configure('value', foreground=INDIGO)
        self.repl.tag_configure('error', foreground=KUMKUM)

        panes.add(top, stretch='always', minsize=120, height=400)
        panes.add(bottom, stretch='always', minsize=100)

    def _build_status(self):
        bar = tk.Frame(self.root, bg=PANEL)
        bar.pack(fill=tk.X, padx=12, pady=(4, 6))
        self.status = tk.Label(bar, font=self.small, bg=PANEL, fg=SOFT, text='ಭಾಷೆ: ಕನ್ನಡ')
        self.status.pack(side=tk.LEFT)
        self.position = tk.Label(bar, font=self.small, bg=PANEL, fg=SOFT)
        self.position.pack(side=tk.RIGHT)

    def _build_menu(self):
        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label='ಹೊಸದು / New', accelerator='Ctrl+N', command=self.new)
        file_menu.add_command(label='ತೆರೆ / Open…', accelerator='Ctrl+O', command=self.open)
        file_menu.add_command(label='ಉಳಿಸು / Save', accelerator='Ctrl+S', command=self.save)
        file_menu.add_command(label='ಹೀಗೆ ಉಳಿಸು / Save As…', command=self.save_as)
        file_menu.add_separator()
        file_menu.add_command(label='ಮುಚ್ಚು / Quit', accelerator='Ctrl+Q', command=self.quit)
        menubar.add_cascade(label='ಕಡತ File', menu=file_menu)

        edit_menu = tk.Menu(menubar, tearoff=0)
        for label, accel, event in (('Undo', 'Ctrl+Z', '<<Undo>>'), ('Redo', 'Ctrl+Y', '<<Redo>>'),
                                    ('Cut', 'Ctrl+X', '<<Cut>>'), ('Copy', 'Ctrl+C', '<<Copy>>'),
                                    ('Paste', 'Ctrl+V', '<<Paste>>')):
            edit_menu.add_command(label=label, accelerator=accel,
                                  command=lambda e=event: self.root.focus_get().event_generate(e))
        menubar.add_cascade(label='ತಿದ್ದು Edit', menu=edit_menu)

        run_menu = tk.Menu(menubar, tearoff=0)
        run_menu.add_command(label='ಓಡಿಸು / Run', accelerator='F5', command=self.run_program)
        run_menu.add_command(label='ನಿಲ್ಲಿಸು / Stop', accelerator='Ctrl+B', command=self.stop)
        menubar.add_cascade(label='ಓಡಿಸು Run', menu=run_menu)

        self.root.config(menu=menubar)

    def _bind_keys(self):
        # Bound on the Text widgets too: Tk's own Ctrl+O/N/B/… would otherwise
        # edit the text as well.
        def bind(sequence, action):
            def handler(_event):
                action()
                return 'break'
            for widget in (self.root, self.editor, self.repl):
                widget.bind(sequence, handler)

        bind('<F5>', self.run_program)
        bind('<Control-r>', self.run_program)
        bind('<Control-b>', self.stop)
        bind('<Control-n>', self.new)
        bind('<Control-o>', self.open)
        bind('<Control-s>', self.save)
        bind('<Control-q>', self.quit)

        self.editor.bind('<<Modified>>', self._on_modified)
        self.editor.bind('<KeyRelease>', self._on_cursor)
        self.editor.bind('<ButtonRelease-1>', self._on_cursor)
        self.editor.bind('<Configure>', lambda _e: self._draw_gutter())
        self.editor.bind('<Tab>', self._on_tab)
        self.editor.bind('<Return>', self._on_editor_return)

        self.repl.bind('<Return>', self._on_repl_return)
        self.repl.bind('<Key>', self._on_repl_key)
        self.repl.bind('<Up>', lambda _e: self._on_history(-1))
        self.repl.bind('<Down>', lambda _e: self._on_history(1))
        self.repl.bind('<Home>', self._on_repl_home)
        self.repl.bind('<<Paste>>', self._on_repl_paste)
        self.repl.bind('<<Cut>>', self._on_repl_cut)

    # === Definitions window ===

    def editor_yview(self, *args):
        self.editor.yview(*args)
        self._draw_gutter()

    def _draw_gutter(self):
        self.gutter.delete('all')
        index = self.editor.index('@0,0')
        while True:
            info = self.editor.dlineinfo(index)
            if info is None:
                break
            self.gutter.create_text(36, info[1] + 3, anchor='ne', text=index.split('.')[0],
                                    fill=SOFT, font=self.small)
            following = self.editor.index(f'{index}+1line')
            if following == index:
                break
            index = following

    def _editor_text(self):
        return self.editor.get('1.0', 'end-1c')

    def _set_editor_text(self, text):
        self.editor.delete('1.0', tk.END)
        self.editor.insert('1.0', text)
        self.editor.edit_reset()
        self.saved_text = text
        self.editor.mark_set('insert', '1.0')
        self._refresh_title()
        self._highlight()
        self._draw_gutter()

    def _on_modified(self, _event=None):
        if not self.editor.edit_modified():
            return
        self.editor.edit_modified(False)
        self.editor.tag_remove('errline', '1.0', tk.END)
        self._refresh_title()
        self._draw_gutter()
        if self._highlight_job:
            self.root.after_cancel(self._highlight_job)
        self._highlight_job = self.root.after(120, self._highlight)

    def _is_dirty(self):
        return self._editor_text() != self.saved_text

    def _refresh_title(self):
        name = os.path.basename(self.path) if self.path else 'ಹೆಸರಿಲ್ಲದ್ದು'
        dirty = self._is_dirty()
        self.name_label.config(text=name + (' *' if dirty else ''))
        self.save_button.config(state=tk.NORMAL if dirty else tk.DISABLED)
        self.root.title(f"{name}{' *' if dirty else ''} - ಕಪಿಲ (Kapila)")

    @staticmethod
    def _line_starts(text):
        starts = [0]
        for match in re.finditer('\n', text):
            starts.append(match.end())
        return starts

    @staticmethod
    def _index(starts, offset):
        line = bisect.bisect_right(starts, offset)
        return f'{line}.{offset - starts[line - 1]}'

    def _highlight(self):
        self._highlight_job = None
        for tag in SYNTAX_TAGS:
            self.editor.tag_remove(tag, '1.0', tk.END)
        text = self._editor_text()
        if len(text) > HIGHLIGHT_LIMIT:
            return

        starts = self._line_starts(text)
        spans = {tag: [] for tag in SYNTAX_TAGS}

        def mark(tag, start, end):
            spans[tag].extend((self._index(starts, start), self._index(starts, end)))

        previous = None     # (start, end) of the last plain word
        for match in TOKEN_RE.finditer(text):
            token, start, end = match.group(), match.start(), match.end()
            if token.startswith('//') or token.startswith('/*'):
                mark('comment', start, end)
            elif token.startswith('"'):
                mark('string', start, end)
            elif token == ':=':
                mark('keyword', start, end)
                if previous:
                    mark('defn', *previous)
            else:
                word = token.rstrip('.॥')
                word_end = start + len(word)
                if word.endswith(':') and len(word) > 1:
                    mark('defn', start, word_end - 1)
                elif NUMBER_RE.match(word):
                    mark('number', start, word_end)
                elif word in VOCABULARY:
                    mark('keyword', start, word_end)
                previous = (start, word_end)
                continue
            previous = None

        for tag, indexes in spans.items():
            if indexes:
                self.editor.tag_add(tag, *indexes)
        self._match_brackets()

    def _match_brackets(self):
        self.editor.tag_remove('bracket_match', '1.0', tk.END)
        text = self._editor_text()
        if len(text) > HIGHLIGHT_LIMIT:
            return
        starts = self._line_starts(text)
        line, col = map(int, self.editor.index('insert').split('.'))
        cursor = starts[line - 1] + col

        here = None
        if cursor < len(text) and text[cursor] in OPENERS:
            here = cursor
        elif cursor > 0 and text[cursor - 1] in CLOSERS:
            here = cursor - 1
        if here is None or self._in_literal(starts, here):
            return

        ch = text[here]
        forward = ch in OPENERS
        partner = OPENERS[ch] if forward else CLOSERS[ch]
        step = 1 if forward else -1
        depth, i = 0, here
        while 0 <= i < len(text):
            if text[i] in (ch, partner) and not self._in_literal(starts, i):
                depth += 1 if text[i] == ch else -1
                if depth == 0:
                    for offset in (here, i):
                        self.editor.tag_add('bracket_match', self._index(starts, offset),
                                            self._index(starts, offset + 1))
                    return
            i += step

    def _in_literal(self, starts, offset):
        tags = self.editor.tag_names(self._index(starts, offset))
        return 'string' in tags or 'comment' in tags

    def _on_cursor(self, _event=None):
        line, col = self.editor.index('insert').split('.')
        self.position.config(text=f'ಸಾಲು {line}, {int(col) + 1}')
        self._match_brackets()

    def _on_tab(self, _event):
        self.editor.insert('insert', '    ')
        return 'break'

    def _on_editor_return(self, _event):
        current = self.editor.get('insert linestart', 'insert')
        indent = current[:len(current) - len(current.lstrip(' '))]
        self.editor.insert('insert', '\n' + indent)
        self.editor.see('insert')
        return 'break'

    # === Files ===

    def _confirm_discard(self):
        """True if it's fine to replace the current text."""
        if not self._is_dirty():
            return True
        name = os.path.basename(self.path) if self.path else 'ಹೆಸರಿಲ್ಲದ್ದು'
        answer = messagebox.askyesnocancel('ಉಳಿಸಬೇಕೇ?', f'Save changes to {name}?')
        if answer is None:
            return False
        return self.save() if answer else True

    def new(self):
        if self._confirm_discard():
            self.path = None
            self._set_editor_text('')
            self.editor.focus_set()

    def open(self):
        if self._confirm_discard():
            path = filedialog.askopenfilename(filetypes=FILE_TYPES)
            if path:
                self._load(path)

    def _load(self, path):
        try:
            with open(path, encoding='utf-8') as f:
                text = f.read()
        except (OSError, UnicodeDecodeError) as e:
            messagebox.showerror('ತೆರೆಯಲಾಗಲಿಲ್ಲ', f'Could not open {path}\n{e}')
            return
        self.path = path
        self._set_editor_text(text)

    def save(self):
        if self.path is None:
            return self.save_as()
        return self._write(self.path)

    def save_as(self):
        path = filedialog.asksaveasfilename(defaultextension='.kpl', filetypes=FILE_TYPES)
        return self._write(path) if path else False

    def _write(self, path):
        text = self._editor_text()
        try:
            with open(path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(text)
        except OSError as e:
            messagebox.showerror('ಉಳಿಸಲಾಗಲಿಲ್ಲ', f'Could not save {path}\n{e}')
            return False
        self.path = path
        self.saved_text = text
        self._refresh_title()
        self.status.config(text=f'ಉಳಿಸಲಾಗಿದೆ: {path}')
        return True

    def quit(self):
        if self.busy:
            self.stop()
        if self._confirm_discard():
            self.root.destroy()

    # === Interactions window ===

    def _append(self, text, tag=None):
        self.repl.insert('end-1c', text, tag or ())
        self.repl.see(tk.END)

    def _reset_repl(self):
        self.repl.delete('1.0', tk.END)
        self._append(f'ಕಪಿಲಕ್ಕೆ ಸ್ವಾಗತ. Welcome to Kapila, version {__version__}.\n'
                     'ಭಾಷೆ: ಕನ್ನಡ.  .s stack   .w words   clear\n', 'banner')

    def _new_prompt(self):
        if self.repl.get('end-2c') != '\n':
            self._append('\n')
        self._append(PROMPT, 'prompt')
        self.repl.mark_set('input', 'end-1c')
        self.repl.mark_gravity('input', tk.LEFT)
        self.repl.mark_set('insert', 'end-1c')
        self.repl.see(tk.END)

    def _has_selection(self):
        return bool(self.repl.tag_ranges('sel'))

    def _selection_touches_output(self):
        return self._has_selection() and self.repl.compare('sel.first', '<', 'input')

    def _on_repl_key(self, event):
        control = event.state & 0x4
        keysym = event.keysym
        if keysym in ('BackSpace', 'Delete') or (control and keysym in ('d', 'h', 't')):
            if self.busy or self._selection_touches_output():
                return 'break'
            if not self._has_selection():
                limit = '<=' if keysym in ('BackSpace', 'h') else '<'
                if self.repl.compare('insert', limit, 'input'):
                    return 'break'
            return None
        if control or not event.char or not event.char.isprintable():
            return None
        if self.busy:
            return 'break'
        self._move_to_input()
        return None

    def _move_to_input(self):
        if self._selection_touches_output():
            self.repl.tag_remove('sel', '1.0', tk.END)
        if self.repl.compare('insert', '<', 'input'):
            self.repl.mark_set('insert', 'end-1c')

    def _on_repl_paste(self, _event):
        if self.busy:
            return 'break'
        self._move_to_input()
        return None

    def _on_repl_cut(self, _event):
        return 'break' if self.busy or self._selection_touches_output() else None

    def _on_repl_home(self, _event):
        if self.repl.compare('insert', '>=', 'input'):
            self.repl.mark_set('insert', 'input')
            return 'break'
        return None

    def _on_history(self, direction):
        if self.repl.compare('insert', '<', 'input'):
            return None
        if self.busy or not self.history:
            return 'break'
        self.history_idx = max(0, min(self.history_idx + direction, len(self.history)))
        text = self.history[self.history_idx] if self.history_idx < len(self.history) else ''
        self.repl.delete('input', 'end-1c')
        self.repl.insert('end-1c', text)
        self.repl.mark_set('insert', 'end-1c')
        self.repl.see(tk.END)
        return 'break'

    def _on_repl_return(self, _event):
        if self.busy:
            return 'break'
        line = self.repl.get('input', 'end-1c').strip()
        self.repl.mark_set('insert', 'end-1c')
        self._append('\n')
        if line:
            self.history.append(line)
            self.history_idx = len(self.history)
            if not self._repl_command(line):
                self._start(line, from_editor=False)
                return 'break'
        self._new_prompt()
        return 'break'

    def _repl_command(self, line):
        """Handle the prompt's own commands. True if line was one."""
        if line == '.s':
            self._append(' '.join(to_kannada(x) for x in self.vm.stack) or '(ಖಾಲಿ)', 'value')
        elif line == '.w':
            self._append(' '.join(self.vm.words.keys()) or '(ಖಾಲಿ)', 'value')
        elif line == 'clear':
            self.vm.stack.clear()
        elif line in ('exit', 'quit'):
            self.quit()
        else:
            return False
        return True

    # === Running ===

    def run_program(self):
        if self.busy:
            return
        self.editor.tag_remove('errline', '1.0', tk.END)
        self.vm = VM()
        self._reset_repl()
        code = self._editor_text()
        if code.strip():
            self._start(code, from_editor=True)
        else:
            self._new_prompt()

    def stop(self):
        if self.busy and self.worker is not None:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(
                ctypes.c_ulong(self.worker.ident), ctypes.py_object(_Stopped))
            self.status.config(text='ನಿಲ್ಲಿಸಲಾಗುತ್ತಿದೆ…')

    def _start(self, code, from_editor):
        self.busy = True
        self.run_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status.config(text='ಓಡುತ್ತಿದೆ…')
        self.worker = threading.Thread(target=self._execute, args=(self.vm, code, from_editor),
                                       daemon=True)
        self.worker.start()
        self.root.after(30, self._poll)

    def _execute(self, vm, code, from_editor):
        """Worker thread. Everything Tk happens back on the main thread."""
        error, line, top, stopped = None, None, None, False
        saved = sys.stdout, sys.stderr, sys.stdin
        try:
            writer = _Writer(self.events)
            sys.stdout, sys.stderr, sys.stdin = writer, writer, _Reader(self)
            before = list(vm.stack)
            try:
                vm.run(code)
            except Exception as e:  # KapilaError, and anything unexpected
                error = e
                line = _error_line(vm, e) if from_editor else None
            else:
                if vm.stack and list(vm.stack) != before:
                    top = to_kannada(vm.stack[-1])
        except _Stopped:
            stopped = True
        finally:
            sys.stdout, sys.stderr, sys.stdin = saved
        self.events.put(('done', top, error, line, stopped, from_editor))

    def _poll(self):
        finished = False
        printed = []   # one insert per tick: a print loop must not starve the window
        for _ in range(POLL_BATCH):
            try:
                event = self.events.get_nowait()
            except queue.Empty:
                break
            if event[0] == 'out':
                printed.append(event[1])
                continue
            if printed:
                self._append(''.join(printed), 'out')
                printed = []
            if event[0] == 'input':
                answer = simpledialog.askstring('ಕಪಿಲ', 'ಮೌಲ್ಯ ನೀಡಿ / Enter a value:', parent=self.root)
                self.answers.put(answer or '')
            else:
                self._finish(*event[1:])
                finished = True
                break
        if printed:
            self._append(''.join(printed), 'out')
        lines = int(self.repl.index('end-1c').split('.')[0])
        if lines > REPL_MAX_LINES:
            self.repl.delete('1.0', f'{lines - REPL_MAX_LINES + 1000}.0')
        if not finished:
            self.root.after(30, self._poll)

    def _finish(self, top, error, line, stopped, from_editor):
        if error is not None:
            if self.repl.get('end-2c') != '\n':
                self._append('\n')
            self._append(f'ದೋಷ: {error}', 'error')
            if line:
                self.editor.tag_add('errline', f'{line}.0', f'{line}.0 lineend+1c')
                self.editor.see(f'{line}.0')
        elif stopped:
            if self.repl.get('end-2c') != '\n':
                self._append('\n')
            self._append('ನಿಲ್ಲಿಸಲಾಗಿದೆ / stopped', 'error')
        elif top is not None:
            if self.repl.get('end-2c') != '\n':
                self._append('\n')
            self._append(f'→ {top}', 'value')

        self.busy = False
        self.worker = None
        self.run_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status.config(text='ಭಾಷೆ: ಕನ್ನಡ')
        self._new_prompt()
        if from_editor and error is None:
            self.repl.focus_set()


def main():
    try:
        # Windows groups the taskbar button by this ID, not by python.exe.
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('matsyaai.kapila.editor')
    except (AttributeError, OSError):
        pass
    root = tk.Tk()
    KapilaGUI(root, sys.argv[1] if len(sys.argv) > 1 else None)
    root.mainloop()


if __name__ == '__main__':
    main()
