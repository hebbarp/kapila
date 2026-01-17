#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ಕಪಿಲ (Kapila) GUI REPL
"""

import tkinter as tk
from tkinter import font as tkfont
import sys
import os
import io

kapila_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, kapila_dir)

from src.vm import VM, KapilaError


class OutputCapture:
    """Capture stdout to a list."""
    def __init__(self):
        self.lines = []

    def write(self, text):
        if text and text.strip():
            self.lines.append(text.rstrip('\n'))

    def flush(self):
        pass

    def get_output(self):
        result = self.lines
        self.lines = []
        return result


def to_kannada(value):
    """Convert value to Kannada representation."""
    if isinstance(value, bool):
        return 'ಸರಿ' if value else 'ತಪ್ಪು'
    if isinstance(value, (int, float)):
        # Convert digits to Kannada
        kannada_digits = '೦೧೨೩೪೫೬೭೮೯'
        s = str(value)
        result = ''
        for ch in s:
            if ch.isdigit():
                result += kannada_digits[int(ch)]
            else:
                result += ch  # keep . and -
        return result
    if isinstance(value, list):
        items = ' '.join(to_kannada(x) for x in value)
        return f'[ {items} ]'
    return str(value)


class KapilaGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ಕಪಿಲ (Kapila)")
        self.root.geometry("700x500")

        self.bg = '#FAF9F6'
        self.root.configure(bg=self.bg)

        self.vm = VM()
        self.history = []
        self.history_idx = 0

        # Font
        self.font = ('Segoe UI', 11)
        for f in ['Noto Sans Kannada', 'Tunga', 'Arial Unicode MS']:
            if f in tkfont.families():
                self.font = (f, 11)
                break

        self._build_ui()

    def _build_ui(self):
        # === INPUT AT TOP ===
        input_frame = tk.Frame(self.root, bg='white', bd=2, relief=tk.SOLID)
        input_frame.pack(fill=tk.X, padx=20, pady=20)

        tk.Label(
            input_frame,
            text=" ಕಪಿಲ> ",
            font=(self.font[0], 12, 'bold'),
            fg='#B8860B',
            bg='white'
        ).pack(side=tk.LEFT)

        self.entry = tk.Entry(
            input_frame,
            font=(self.font[0], 12),
            bg='white',
            fg='black',
            relief=tk.FLAT,
            bd=0,
            insertbackground='black'
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        self.entry.bind('<Return>', self._run)
        self.entry.bind('<Up>', self._hist_up)
        self.entry.bind('<Down>', self._hist_down)
        self.entry.focus_set()

        # === OUTPUT BELOW ===
        self.output = tk.Text(
            self.root,
            font=self.font,
            bg=self.bg,
            fg='#1a1a1a',
            wrap=tk.WORD,
            padx=15,
            pady=15,
            relief=tk.FLAT,
            state=tk.DISABLED,
            cursor="arrow"
        )
        self.output.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        self.output.tag_configure('prompt', foreground='#B8860B')
        self.output.tag_configure('result', foreground='#2E8B57')
        self.output.tag_configure('error', foreground='#CD5C5C')

        self._print("ಫಲಿತಾಂಶ:\n\n")

    def _print(self, text, tag=None):
        self.output.config(state=tk.NORMAL)
        if tag:
            self.output.insert(tk.END, text, tag)
        else:
            self.output.insert(tk.END, text)
        self.output.see(tk.END)
        self.output.config(state=tk.DISABLED)

    def _run(self, event):
        line = self.entry.get().strip()
        self.entry.delete(0, tk.END)

        if not line:
            return

        self.history.append(line)
        self.history_idx = len(self.history)

        self._print(f"ಕಪಿಲ> {line}\n", 'prompt')

        if line in ('exit', 'quit'):
            self.root.quit()
            return
        if line == '.s':
            stack_kannada = [to_kannada(x) for x in self.vm.stack]
            self._print(f"  {stack_kannada}\n\n")
            return
        if line == '.w':
            self._print(f"  {list(self.vm.words.keys())}\n\n")
            return
        if line == 'clear':
            self.vm.stack.clear()
            self._print("  cleared\n\n")
            return

        try:
            # Capture stdout to show print output in GUI
            capture = OutputCapture()
            old_stdout = sys.stdout
            sys.stdout = capture

            try:
                self.vm.run(line)
            finally:
                sys.stdout = old_stdout

            # Show any printed output
            for output_line in capture.get_output():
                kannada_output = to_kannada(output_line) if isinstance(output_line, (int, float, bool)) else output_line
                self._print(f"  {kannada_output}\n", 'result')

            # Show stack result if any
            if self.vm.stack:
                result = to_kannada(self.vm.stack[-1])
                self._print(f"  → {result}\n\n", 'result')
            else:
                self._print("\n")

        except KapilaError as e:
            sys.stdout = old_stdout if 'old_stdout' in dir() else sys.stdout
            self._print(f"  ದೋಷ: {e}\n\n", 'error')
        except Exception as e:
            sys.stdout = old_stdout if 'old_stdout' in dir() else sys.stdout
            self._print(f"  ದೋಷ: {e}\n\n", 'error')

    def _hist_up(self, event):
        if self.history and self.history_idx > 0:
            self.history_idx -= 1
            self.entry.delete(0, tk.END)
            self.entry.insert(0, self.history[self.history_idx])

    def _hist_down(self, event):
        if self.history_idx < len(self.history) - 1:
            self.history_idx += 1
            self.entry.delete(0, tk.END)
            self.entry.insert(0, self.history[self.history_idx])
        else:
            self.history_idx = len(self.history)
            self.entry.delete(0, tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    KapilaGUI(root)
    root.mainloop()
