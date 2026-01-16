# -*- coding: utf-8 -*-
"""
Kapila Built-in Words
=====================

Core words that are implemented in Python.

Stack effect notation: ( before -- after )
Example: ( a b -- sum )  means takes a, b from stack, leaves sum
"""


def builtin_add(vm):
    """( a b -- a+b ) Addition."""
    b = vm.pop()
    a = vm.pop()
    vm.push(a + b)


def builtin_sub(vm):
    """( a b -- a-b ) Subtraction."""
    b = vm.pop()
    a = vm.pop()
    vm.push(a - b)


def builtin_mul(vm):
    """( a b -- a*b ) Multiplication."""
    b = vm.pop()
    a = vm.pop()
    vm.push(a * b)


def builtin_div(vm):
    """( a b -- a/b ) Division."""
    b = vm.pop()
    a = vm.pop()
    vm.push(a / b)


def builtin_mod(vm):
    """( a b -- a%b ) Modulo."""
    b = vm.pop()
    a = vm.pop()
    vm.push(a % b)


def builtin_eq(vm):
    """( a b -- bool ) Equal."""
    b = vm.pop()
    a = vm.pop()
    vm.push(a == b)


def builtin_neq(vm):
    """( a b -- bool ) Not equal."""
    b = vm.pop()
    a = vm.pop()
    vm.push(a != b)


def builtin_lt(vm):
    """( a b -- bool ) Less than."""
    b = vm.pop()
    a = vm.pop()
    vm.push(a < b)


def builtin_gt(vm):
    """( a b -- bool ) Greater than."""
    b = vm.pop()
    a = vm.pop()
    vm.push(a > b)


def builtin_lte(vm):
    """( a b -- bool ) Less than or equal."""
    b = vm.pop()
    a = vm.pop()
    vm.push(a <= b)


def builtin_gte(vm):
    """( a b -- bool ) Greater than or equal."""
    b = vm.pop()
    a = vm.pop()
    vm.push(a >= b)


# === Stack manipulation ===

def builtin_dup(vm):
    """( a -- a a ) Duplicate top."""
    a = vm.pop()
    vm.push(a)
    vm.push(a)


def builtin_drop(vm):
    """( a -- ) Discard top."""
    vm.pop()


def builtin_swap(vm):
    """( a b -- b a ) Swap top two."""
    b = vm.pop()
    a = vm.pop()
    vm.push(b)
    vm.push(a)


def builtin_over(vm):
    """( a b -- a b a ) Copy second to top."""
    b = vm.pop()
    a = vm.pop()
    vm.push(a)
    vm.push(b)
    vm.push(a)


def builtin_rot(vm):
    """( a b c -- b c a ) Rotate three."""
    c = vm.pop()
    b = vm.pop()
    a = vm.pop()
    vm.push(b)
    vm.push(c)
    vm.push(a)


# === I/O ===

def builtin_print(vm):
    """( a -- ) Print top of stack."""
    a = vm.pop()
    print(a)


def builtin_println(vm):
    """( a -- ) Print with newline."""
    a = vm.pop()
    print(a)


def builtin_show_stack(vm):
    """( -- ) Show current stack (for debugging)."""
    print(f"Stack: {vm.stack}")


# === Logic ===

def builtin_and(vm):
    """( a b -- bool ) Logical and."""
    b = vm.pop()
    a = vm.pop()
    vm.push(a and b)


def builtin_or(vm):
    """( a b -- bool ) Logical or."""
    b = vm.pop()
    a = vm.pop()
    vm.push(a or b)


def builtin_not(vm):
    """( a -- bool ) Logical not."""
    a = vm.pop()
    vm.push(not a)


# === List operations ===

def builtin_list_length(vm):
    """( list -- n ) Length of list."""
    lst = vm.pop()
    vm.push(len(lst))


def builtin_list_get(vm):
    """( list n -- item ) Get nth item."""
    n = vm.pop()
    lst = vm.pop()
    vm.push(lst[int(n)])


def builtin_list_append(vm):
    """( list item -- newlist ) Append item (immutable)."""
    item = vm.pop()
    lst = vm.pop()
    vm.push(lst + [item])


def builtin_list_first(vm):
    """( list -- item ) First item."""
    lst = vm.pop()
    vm.push(lst[0])


def builtin_list_rest(vm):
    """( list -- rest ) All but first."""
    lst = vm.pop()
    vm.push(lst[1:])


# === String operations ===

def builtin_str_length(vm):
    """( str -- n ) String length."""
    s = vm.pop()
    vm.push(len(s))


def builtin_str_concat(vm):
    """( a b -- ab ) Concatenate strings."""
    b = vm.pop()
    a = vm.pop()
    vm.push(str(a) + str(b))


# === Higher-order ===

def builtin_map(vm):
    """( list quot -- newlist ) Map quotation over list."""
    quot = vm.pop()
    lst = vm.pop()
    result = []
    for item in lst:
        vm.push(item)
        vm.execute_quotation(quot)
        result.append(vm.pop())
    vm.push(result)


def builtin_filter(vm):
    """( list quot -- newlist ) Filter list by quotation."""
    quot = vm.pop()
    lst = vm.pop()
    result = []
    for item in lst:
        vm.push(item)
        vm.execute_quotation(quot)
        if vm.pop():
            result.append(item)
    vm.push(result)


def builtin_fold(vm):
    """( list init quot -- result ) Fold/reduce list."""
    quot = vm.pop()
    acc = vm.pop()
    lst = vm.pop()
    for item in lst:
        vm.push(acc)
        vm.push(item)
        vm.execute_quotation(quot)
        acc = vm.pop()
    vm.push(acc)


def builtin_each(vm):
    """( list quot -- ) Execute quotation for each item."""
    quot = vm.pop()
    lst = vm.pop()
    for item in lst:
        vm.push(item)
        vm.execute_quotation(quot)


def builtin_times(vm):
    """( n quot -- ) Execute quotation n times."""
    quot = vm.pop()
    n = int(vm.pop())
    for i in range(n):
        vm.push(i)
        vm.execute_quotation(quot)
        vm.pop()  # discard the loop index


def builtin_do(vm):
    """( quot -- ... ) Execute quotation."""
    quot = vm.pop()
    vm.execute_quotation(quot)


# === Boolean builtins (push literal values) ===

def builtin_true(vm):
    """( -- true ) Push true."""
    vm.push(True)


def builtin_false(vm):
    """( -- false ) Push false."""
    vm.push(False)


# === Built-in registry ===
# Core English builtins - Kannada aliases are added from vocabulary.py

_CORE_BUILTINS = {
    # Arithmetic
    '+': builtin_add,
    '-': builtin_sub,
    '*': builtin_mul,
    '/': builtin_div,
    '%': builtin_mod,

    # Comparison
    '=': builtin_eq,
    '!=': builtin_neq,
    '≠': builtin_neq,
    '<': builtin_lt,
    '>': builtin_gt,
    '<=': builtin_lte,
    '≤': builtin_lte,
    '>=': builtin_gte,
    '≥': builtin_gte,

    # Stack
    'dup': builtin_dup,
    'drop': builtin_drop,
    'swap': builtin_swap,
    'over': builtin_over,
    'rot': builtin_rot,

    # I/O
    'print': builtin_print,
    '.s': builtin_show_stack,

    # Logic
    'and': builtin_and,
    'or': builtin_or,
    'not': builtin_not,

    # Boolean literals (as operations)
    'true': builtin_true,
    'false': builtin_false,

    # List
    'length': builtin_list_length,
    'nth': builtin_list_get,
    'append': builtin_list_append,
    'first': builtin_list_first,
    'rest': builtin_list_rest,

    # String
    ',': builtin_str_concat,

    # Higher-order
    'map': builtin_map,
    'filter': builtin_filter,
    'fold': builtin_fold,
    'each': builtin_each,
    'times': builtin_times,
    'do': builtin_do,
}


def _build_builtins():
    """Build complete builtins dict with Kannada vocabulary."""
    builtins = dict(_CORE_BUILTINS)

    # Import vocabulary and add Kannada aliases
    try:
        from ..vocabulary import VOCABULARY
        for kannada_word, english_equiv in VOCABULARY.items():
            if english_equiv in builtins:
                builtins[kannada_word] = builtins[english_equiv]
    except ImportError:
        # Fallback if vocabulary not available
        pass

    return builtins


BUILTINS = _build_builtins()
