# -*- coding: utf-8 -*-
"""
Sandarbha (ಸಂದರ್ಭ) — Context Store
=====================================

Maintains a running context of role→value and type→value bindings
so that underspecified Kannada commands can resolve missing slots
from prior statements.

Key operations:
    record(value, role, type_tag)  — store a resolved binding
    query_role(role) → value       — most recent value for a role
    query_type(type_tag) → value   — most recent value of a type
    push_scope() / pop_scope()     — block boundary management
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ContextEntry:
    """A single recorded binding."""
    value: Any
    role: str
    type_tag: Optional[str]
    tick: int
    scope_depth: int


class Sandarbha:
    """Accumulating context store for implicit slot resolution."""

    def __init__(self):
        self._roles: Dict[str, Any] = {}         # role → most recent value
        self._types: Dict[str, Any] = {}          # type_tag → most recent value
        self._history: List[ContextEntry] = []    # all entries with timestamps
        self._clock: int = 0                      # monotonic counter
        self._scope_depth: int = 0                # current scope depth

    def record(self, value: Any, role: str, type_tag: Optional[str] = None):
        """Store a resolved binding in the context.

        Args:
            value: The resolved value.
            role: Semantic role (e.g. 'ವಸ್ತು', 'ಗಮ್ಯ', 'ಸಾಧನ', 'ಸ್ಥಳ').
            type_tag: Optional type hint (e.g. 'ಕಡತ', 'ವ್ಯಕ್ತಿ').
        """
        self._clock += 1
        entry = ContextEntry(
            value=value,
            role=role,
            type_tag=type_tag,
            tick=self._clock,
            scope_depth=self._scope_depth,
        )
        self._history.append(entry)
        self._roles[role] = value
        if type_tag:
            self._types[type_tag] = value

    def query_role(self, role: str) -> Optional[Any]:
        """Get the most recent value for a semantic role.

        Args:
            role: Semantic role to look up.

        Returns:
            The most recent value, or None if no binding exists.
        """
        return self._roles.get(role)

    def query_type(self, type_tag: str) -> Optional[Any]:
        """Get the most recent value of a given type.

        Args:
            type_tag: Type tag to look up.

        Returns:
            The most recent value, or None if no binding exists.
        """
        return self._types.get(type_tag)

    def query_role_with_type(self, role: str, type_constraint: str) -> Optional[Any]:
        """Query for a role, preferring values that match a type constraint.

        If type_constraint is '*', just query by role.
        Otherwise, try type_constraint first, then fall back to role.

        Args:
            role: The semantic role.
            type_constraint: Type constraint ('*' means any).

        Returns:
            Best matching value, or None.
        """
        if type_constraint == '*':
            return self.query_role(role)

        # Try type-constrained lookup first
        type_val = self.query_type(type_constraint)
        if type_val is not None:
            return type_val

        # Fall back to role-only lookup
        return self.query_role(role)

    def push_scope(self):
        """Enter a new block scope."""
        self._scope_depth += 1

    def pop_scope(self):
        """Exit a block scope."""
        if self._scope_depth > 0:
            self._scope_depth -= 1

    def clear(self):
        """Reset all context (e.g. between REPL sessions)."""
        self._roles.clear()
        self._types.clear()
        self._history.clear()
        self._clock = 0
        self._scope_depth = 0
