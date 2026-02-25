# -*- coding: utf-8 -*-
"""
Sandarbha (ಸಂದರ್ಭ) — Context Resolver for Kapila
==================================================

Resolves underspecified Kannada commands by:
  1. Analyzing vibhakti (case suffixes) to label semantic roles
  2. Accumulating resolved values in a context store
  3. Filling missing verb slots from context

Exports:
    Sandarbha        — Context store class
    analyze_vibhakti — Vibhakti suffix analyzer
    VERB_FRAMES      — Verb frame registry
    NOUN_TYPE_MAP    — Noun → type mapping
    infer_type       — Type inference helper
"""

from .vibhakti import analyze_vibhakti, VibhaktiResult
from .context import Sandarbha
from .frames import VERB_FRAMES, NOUN_TYPE_MAP, infer_type

__all__ = [
    'Sandarbha',
    'analyze_vibhakti',
    'VibhaktiResult',
    'VERB_FRAMES',
    'NOUN_TYPE_MAP',
    'infer_type',
]
