# -*- coding: utf-8 -*-
"""
Execution trace (ಹಂತಗಳು, "steps") — what a run actually did.

When vm.trace is a list (the web playground sets it), every word executed and
every request a source sends to the outside world is appended to it, so the
playground can show the real steps behind the output. vm.trace = None (the
default) turns tracing off at no cost.

Entry shapes:
    {"k": "word",  "d": depth, "w": name, "in": top-before, "out": top-after}
    {"k": "fetch", "d": depth, "host": ..., "path": ..., "cached": bool, "ms": int, "bytes": int}
    {"k": "fetch", ..., "error": message}
"""

TRACE_LIMIT = 300     # entries kept per run; the rest are only counted


def add(vm, entry: dict):
    """Append an entry if tracing is on; returns it (or None if not kept)."""
    trace = getattr(vm, "trace", None)
    if trace is None:
        return None
    if len(trace) >= TRACE_LIMIT:
        vm.trace_dropped = getattr(vm, "trace_dropped", 0) + 1
        return None
    entry["d"] = getattr(vm, "_trace_depth", 0)
    trace.append(entry)
    return entry


def summarize(value) -> str:
    """Short description of a value for one trace line."""
    from .vm import Block
    if isinstance(value, bool):
        return "ನಿಜ" if value else "ಸುಳ್ಳು"
    if isinstance(value, (int, float)):
        return f"{value:g}" if isinstance(value, float) else str(value)
    if isinstance(value, str):
        s = value if len(value) <= 40 else value[:39] + "…"
        return f'"{s}"'
    if isinstance(value, dict):
        return f"ದಾಖಲೆ ({len(value)} ಕ್ಷೇತ್ರ)"
    if isinstance(value, list):
        if value and all(isinstance(v, dict) for v in value):
            return f"ದಾಖಲೆಗಳ ಪಟ್ಟಿ ({len(value)})"
        if len(value) <= 6:
            return "[" + " ".join(summarize(v) for v in value) + "]"
        return f"ಪಟ್ಟಿ ({len(value)})"
    if isinstance(value, Block):
        return "[ … ]"
    if value is None:
        return "ಏನೂ ಇಲ್ಲ"
    s = str(value)
    return s if len(s) <= 40 else s[:39] + "…"
