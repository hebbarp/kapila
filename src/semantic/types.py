# -*- coding: utf-8 -*-
"""
Kapila Type System
==================

Core types for the Kapila language.

Types (Kannada names):
    ಸಂಖ್ಯೆ      (Sankhye)      - Number (int or float)
    ಪೂರ್ಣಾಂಕ    (Purnanka)     - Integer
    ದಶಮಾಂಶ     (Dashamansha)  - Float/Decimal
    ಪಠ್ಯ        (Pathya)       - String/Text
    ಬೂಲ್        (Bool)         - Boolean
    ಪಟ್ಟಿ       (Patti)        - List
    ನಕ್ಷೆ       (Nakshe)       - Map/Dictionary
    ಖಂಡ        (Khanda)       - Block/Function
    ಶೂನ್ಯ       (Shunya)       - Void/Nothing
    ಯಾವುದಾದರೂ  (Yaavudaadaroo) - Any type
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from abc import ABC, abstractmethod


# =============================================================================
# BASE TYPE
# =============================================================================

@dataclass
class Type(ABC):
    """Base class for all types."""

    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def kannada_name(self) -> str:
        """Return Kannada name of the type."""
        pass

    def is_numeric(self) -> bool:
        """Check if this is a numeric type."""
        return False

    def is_compatible(self, other: 'Type') -> bool:
        """Check if this type is compatible with another."""
        if isinstance(other, AnyType):
            return True
        return type(self) == type(other)


# =============================================================================
# PRIMITIVE TYPES
# =============================================================================

@dataclass
class IntType(Type):
    """Integer type - ಪೂರ್ಣಾಂಕ"""

    def __str__(self) -> str:
        return "Int"

    def kannada_name(self) -> str:
        return "ಪೂರ್ಣಾಂಕ"

    def is_numeric(self) -> bool:
        return True

    def is_compatible(self, other: Type) -> bool:
        if isinstance(other, (AnyType, IntType, NumberType)):
            return True
        return False


@dataclass
class FloatType(Type):
    """Float type - ದಶಮಾಂಶ"""

    def __str__(self) -> str:
        return "Float"

    def kannada_name(self) -> str:
        return "ದಶಮಾಂಶ"

    def is_numeric(self) -> bool:
        return True

    def is_compatible(self, other: Type) -> bool:
        if isinstance(other, (AnyType, FloatType, NumberType)):
            return True
        return False


@dataclass
class NumberType(Type):
    """Generic number type - ಸಂಖ್ಯೆ (can be int or float)"""

    def __str__(self) -> str:
        return "Number"

    def kannada_name(self) -> str:
        return "ಸಂಖ್ಯೆ"

    def is_numeric(self) -> bool:
        return True

    def is_compatible(self, other: Type) -> bool:
        if isinstance(other, (AnyType, IntType, FloatType, NumberType)):
            return True
        return False


@dataclass
class StringType(Type):
    """String type - ಪಠ್ಯ"""

    def __str__(self) -> str:
        return "String"

    def kannada_name(self) -> str:
        return "ಪಠ್ಯ"


@dataclass
class BoolType(Type):
    """Boolean type - ಬೂಲ್"""

    def __str__(self) -> str:
        return "Bool"

    def kannada_name(self) -> str:
        return "ಬೂಲ್"


@dataclass
class VoidType(Type):
    """Void/Nothing type - ಶೂನ್ಯ"""

    def __str__(self) -> str:
        return "Void"

    def kannada_name(self) -> str:
        return "ಶೂನ್ಯ"


@dataclass
class AnyType(Type):
    """Any type - ಯಾವುದಾದರೂ (used for type inference)"""

    def __str__(self) -> str:
        return "Any"

    def kannada_name(self) -> str:
        return "ಯಾವುದಾದರೂ"

    def is_compatible(self, other: Type) -> bool:
        return True  # Any is compatible with everything


# =============================================================================
# COMPOUND TYPES
# =============================================================================

@dataclass
class ListType(Type):
    """List type - ಪಟ್ಟಿ"""
    element_type: Type = field(default_factory=AnyType)

    def __str__(self) -> str:
        return f"List[{self.element_type}]"

    def kannada_name(self) -> str:
        return f"ಪಟ್ಟಿ[{self.element_type.kannada_name()}]"

    def is_compatible(self, other: Type) -> bool:
        if isinstance(other, AnyType):
            return True
        if isinstance(other, ListType):
            return self.element_type.is_compatible(other.element_type)
        return False


@dataclass
class MapType(Type):
    """Map/Dictionary type - ನಕ್ಷೆ"""
    key_type: Type = field(default_factory=StringType)
    value_type: Type = field(default_factory=AnyType)

    def __str__(self) -> str:
        return f"Map[{self.key_type}, {self.value_type}]"

    def kannada_name(self) -> str:
        return f"ನಕ್ಷೆ[{self.key_type.kannada_name()}, {self.value_type.kannada_name()}]"

    def is_compatible(self, other: Type) -> bool:
        if isinstance(other, AnyType):
            return True
        if isinstance(other, MapType):
            return (self.key_type.is_compatible(other.key_type) and
                    self.value_type.is_compatible(other.value_type))
        return False


@dataclass
class BlockType(Type):
    """Block/Function type - ಖಂಡ"""
    param_types: List[Type] = field(default_factory=list)
    return_type: Type = field(default_factory=AnyType)
    # Stack effect: how many items consumed and produced
    consumes: int = 0  # items popped from stack
    produces: int = 0  # items pushed to stack

    def __str__(self) -> str:
        params = ", ".join(str(t) for t in self.param_types)
        return f"Block({params}) -> {self.return_type}"

    def kannada_name(self) -> str:
        params = ", ".join(t.kannada_name() for t in self.param_types)
        return f"ಖಂಡ({params}) -> {self.return_type.kannada_name()}"

    def stack_effect(self) -> str:
        """Forth-style stack effect notation."""
        return f"( {self.consumes} -- {self.produces} )"

    def is_compatible(self, other: Type) -> bool:
        if isinstance(other, AnyType):
            return True
        if isinstance(other, BlockType):
            if len(self.param_types) != len(other.param_types):
                return False
            for p1, p2 in zip(self.param_types, other.param_types):
                if not p1.is_compatible(p2):
                    return False
            return self.return_type.is_compatible(other.return_type)
        return False


# =============================================================================
# TYPE SINGLETONS
# =============================================================================

# Commonly used type instances
INT = IntType()
FLOAT = FloatType()
NUMBER = NumberType()
STRING = StringType()
BOOL = BoolType()
VOID = VoidType()
ANY = AnyType()


# =============================================================================
# TYPE UTILITIES
# =============================================================================

def type_from_value(value) -> Type:
    """Infer type from a Python value."""
    if isinstance(value, bool):
        return BOOL
    if isinstance(value, int):
        return INT
    if isinstance(value, float):
        return FLOAT
    if isinstance(value, str):
        return STRING
    if isinstance(value, list):
        if not value:
            return ListType(ANY)
        # Infer element type from first element
        elem_type = type_from_value(value[0])
        return ListType(elem_type)
    if isinstance(value, dict):
        return MapType(STRING, ANY)
    return ANY


def common_type(t1: Type, t2: Type) -> Type:
    """Find common type for two types (for type inference)."""
    if isinstance(t1, AnyType):
        return t2
    if isinstance(t2, AnyType):
        return t1
    if type(t1) == type(t2):
        return t1
    # Numeric promotion
    if t1.is_numeric() and t2.is_numeric():
        if isinstance(t1, FloatType) or isinstance(t2, FloatType):
            return FLOAT
        return NUMBER
    return ANY


# =============================================================================
# SYMBOL TABLE
# =============================================================================

@dataclass
class Symbol:
    """A symbol in the symbol table."""
    name: str
    type: Type
    is_builtin: bool = False
    is_mutable: bool = True


class SymbolTable:
    """Symbol table for type checking."""

    def __init__(self, parent: Optional['SymbolTable'] = None):
        self.symbols: Dict[str, Symbol] = {}
        self.parent = parent

    def define(self, name: str, type: Type, is_builtin: bool = False):
        """Define a symbol."""
        self.symbols[name] = Symbol(name, type, is_builtin)

    def lookup(self, name: str) -> Optional[Symbol]:
        """Look up a symbol."""
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.lookup(name)
        return None

    def is_defined(self, name: str) -> bool:
        """Check if symbol is defined."""
        return self.lookup(name) is not None

    def create_child(self) -> 'SymbolTable':
        """Create a child scope."""
        return SymbolTable(parent=self)


# =============================================================================
# BUILTIN TYPES
# =============================================================================

def create_builtin_symbols() -> SymbolTable:
    """Create symbol table with builtin word types."""
    table = SymbolTable()

    # Stack operations: ( a -- a a )
    dup_type = BlockType(consumes=1, produces=2)
    table.define('dup', dup_type, is_builtin=True)
    table.define('ನಕಲು', dup_type, is_builtin=True)

    # ( a -- )
    drop_type = BlockType(consumes=1, produces=0)
    table.define('drop', drop_type, is_builtin=True)
    table.define('ಬಿಡು', drop_type, is_builtin=True)

    # ( a b -- b a )
    swap_type = BlockType(consumes=2, produces=2)
    table.define('swap', swap_type, is_builtin=True)
    table.define('ಅದಲುಬದಲು', swap_type, is_builtin=True)

    # Arithmetic: ( num num -- num )
    arith_type = BlockType(
        param_types=[NUMBER, NUMBER],
        return_type=NUMBER,
        consumes=2,
        produces=1
    )
    for name in ['+', '-', '*', '/', '%',
                 'ಕೂಡು', 'ಕಳೆ', 'ಗುಣಿಸು', 'ಭಾಗಿಸು']:
        table.define(name, arith_type, is_builtin=True)

    # Comparison: ( num num -- bool )
    cmp_type = BlockType(
        param_types=[NUMBER, NUMBER],
        return_type=BOOL,
        consumes=2,
        produces=1
    )
    for name in ['<', '>', '=', '!=', '<=', '>=',
                 'ಕಿರಿದು', 'ಹಿರಿದು', 'ಸಮ']:
        table.define(name, cmp_type, is_builtin=True)

    # Logic: ( bool bool -- bool )
    logic_type = BlockType(
        param_types=[BOOL, BOOL],
        return_type=BOOL,
        consumes=2,
        produces=1
    )
    for name in ['and', 'or', 'ಮತ್ತು', 'ಅಥವಾ']:
        table.define(name, logic_type, is_builtin=True)

    # Not: ( bool -- bool )
    not_type = BlockType(
        param_types=[BOOL],
        return_type=BOOL,
        consumes=1,
        produces=1
    )
    table.define('not', not_type, is_builtin=True)
    table.define('ಅಲ್ಲ', not_type, is_builtin=True)

    # Print: ( a -- )
    print_type = BlockType(consumes=1, produces=0)
    table.define('print', print_type, is_builtin=True)
    table.define('ಮುದ್ರಿಸು', print_type, is_builtin=True)

    return table
