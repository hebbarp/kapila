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


def builtin_abs(vm):
    """( n -- |n| ) Absolute value."""
    a = vm.pop()
    vm.push(abs(a))


def builtin_min(vm):
    """( a b -- min ) Minimum of two values."""
    b = vm.pop()
    a = vm.pop()
    vm.push(min(a, b))


def builtin_max(vm):
    """( a b -- max ) Maximum of two values."""
    b = vm.pop()
    a = vm.pop()
    vm.push(max(a, b))


def builtin_pow(vm):
    """( base exp -- result ) Raise base to power."""
    import math
    exp = vm.pop()
    base = vm.pop()
    vm.push(math.pow(base, exp))


def builtin_sqrt(vm):
    """( n -- sqrt ) Square root."""
    import math
    a = vm.pop()
    vm.push(math.sqrt(a))


def builtin_floor(vm):
    """( n -- floor ) Floor of number."""
    import math
    a = vm.pop()
    vm.push(math.floor(a))


def builtin_ceil(vm):
    """( n -- ceil ) Ceiling of number."""
    import math
    a = vm.pop()
    vm.push(math.ceil(a))


def builtin_round(vm):
    """( n -- rounded ) Round to nearest integer."""
    a = vm.pop()
    vm.push(round(a))


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


def builtin_list_last(vm):
    """( list -- item ) Last item."""
    lst = vm.pop()
    vm.push(lst[-1])


def builtin_list_reverse(vm):
    """( list -- reversed ) Reverse list."""
    lst = vm.pop()
    vm.push(list(reversed(lst)))


def builtin_list_sort(vm):
    """( list -- sorted ) Sort list."""
    lst = vm.pop()
    vm.push(sorted(lst))


def builtin_list_empty(vm):
    """( list -- bool ) Check if list is empty."""
    lst = vm.pop()
    vm.push(len(lst) == 0)


def builtin_list_concat(vm):
    """( list1 list2 -- combined ) Concatenate two lists."""
    lst2 = vm.pop()
    lst1 = vm.pop()
    vm.push(lst1 + lst2)


def builtin_list_take(vm):
    """( list n -- sublist ) Take first n items."""
    n = int(vm.pop())
    lst = vm.pop()
    vm.push(lst[:n])


def builtin_list_drop(vm):
    """( list n -- sublist ) Drop first n items."""
    n = int(vm.pop())
    lst = vm.pop()
    vm.push(lst[n:])


def builtin_list_contains(vm):
    """( list item -- bool ) Check if list contains item."""
    item = vm.pop()
    lst = vm.pop()
    vm.push(item in lst)


def builtin_list_index(vm):
    """( list item -- index ) Find index of item (-1 if not found)."""
    item = vm.pop()
    lst = vm.pop()
    try:
        vm.push(lst.index(item))
    except ValueError:
        vm.push(-1)


def builtin_range(vm):
    """( start end -- list ) Create range from start to end-1."""
    end = int(vm.pop())
    start = int(vm.pop())
    vm.push(list(range(start, end)))


def builtin_range_single(vm):
    """( n -- list ) Create range from 0 to n-1."""
    n = int(vm.pop())
    vm.push(list(range(n)))


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


def builtin_str_split(vm):
    """( str delim -- list ) Split string by delimiter."""
    delim = vm.pop()
    s = vm.pop()
    vm.push(s.split(delim))


def builtin_str_join(vm):
    """( list delim -- str ) Join list with delimiter."""
    delim = vm.pop()
    lst = vm.pop()
    vm.push(delim.join(str(x) for x in lst))


def builtin_str_substring(vm):
    """( str start end -- substr ) Get substring."""
    end = int(vm.pop())
    start = int(vm.pop())
    s = vm.pop()
    vm.push(s[start:end])


def builtin_str_find(vm):
    """( str pattern -- index ) Find pattern in string (-1 if not found)."""
    pattern = vm.pop()
    s = vm.pop()
    vm.push(s.find(pattern))


def builtin_str_replace(vm):
    """( str old new -- newstr ) Replace all occurrences."""
    new = vm.pop()
    old = vm.pop()
    s = vm.pop()
    vm.push(s.replace(old, new))


def builtin_str_trim(vm):
    """( str -- trimmed ) Remove leading/trailing whitespace."""
    s = vm.pop()
    vm.push(s.strip())


def builtin_str_upper(vm):
    """( str -- upper ) Convert to uppercase."""
    s = vm.pop()
    vm.push(s.upper())


def builtin_str_lower(vm):
    """( str -- lower ) Convert to lowercase."""
    s = vm.pop()
    vm.push(s.lower())


def builtin_str_starts(vm):
    """( str prefix -- bool ) Check if string starts with prefix."""
    prefix = vm.pop()
    s = vm.pop()
    vm.push(s.startswith(prefix))


def builtin_str_ends(vm):
    """( str suffix -- bool ) Check if string ends with suffix."""
    suffix = vm.pop()
    s = vm.pop()
    vm.push(s.endswith(suffix))


def builtin_str_contains(vm):
    """( str substr -- bool ) Check if string contains substring."""
    substr = vm.pop()
    s = vm.pop()
    vm.push(substr in s)


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


def builtin_read_line(vm):
    """( -- str ) Read a line from stdin."""
    line = input()
    vm.push(line)


def builtin_to_string(vm):
    """( a -- str ) Convert top of stack to string."""
    a = vm.pop()
    vm.push(str(a))


def builtin_to_int(vm):
    """( a -- int ) Convert top of stack to integer."""
    a = vm.pop()
    vm.push(int(a))


def builtin_to_float(vm):
    """( a -- float ) Convert top of stack to float."""
    a = vm.pop()
    vm.push(float(a))


def builtin_while(vm):
    """( cond-block body-block -- ) While loop.

    Executes body-block while cond-block returns true.
    Example: [ i 10 < ] [ i ಮುದ್ರಿಸು i 1 + i := ] while
    """
    body = vm.pop()
    cond = vm.pop()

    while True:
        vm.execute_quotation(cond)
        if not vm.pop():
            break
        vm.execute_quotation(body)


def builtin_until(vm):
    """( cond-block body-block -- ) Until loop.

    Executes body-block until cond-block returns true.
    """
    body = vm.pop()
    cond = vm.pop()

    while True:
        vm.execute_quotation(cond)
        if vm.pop():
            break
        vm.execute_quotation(body)


def builtin_loop(vm):
    """( body-block -- ) Infinite loop (use with break).

    Note: Currently no break support, so this will loop forever.
    Use while/until with condition instead.
    """
    body = vm.pop()
    while True:
        vm.execute_quotation(body)


def builtin_if(vm):
    """( bool then-block -- ) Conditional execution.

    Executes then-block if bool is true.
    """
    then_block = vm.pop()
    cond = vm.pop()
    if cond:
        vm.execute_quotation(then_block)


def builtin_ifelse(vm):
    """( bool then-block else-block -- ) Conditional with else.

    Executes then-block if true, else-block if false.
    """
    else_block = vm.pop()
    then_block = vm.pop()
    cond = vm.pop()
    if cond:
        vm.execute_quotation(then_block)
    else:
        vm.execute_quotation(else_block)


# === Metaprogramming ===

def builtin_eval(vm):
    """( string -- ... ) Evaluate string as Kapila code."""
    code = vm.pop()
    # Save outer execution state (vm.run overwrites tokens/pos)
    saved_tokens = getattr(vm, 'tokens', None)
    saved_pos = getattr(vm, 'pos', None)
    vm.run(code)
    # Restore outer execution state
    if saved_tokens is not None:
        vm.tokens = saved_tokens
        vm.pos = saved_pos


def builtin_code_string(vm):
    """( block -- string ) Convert block to source string."""
    block = vm.pop()
    source = " ".join(t.value for t in block.tokens)
    vm.push(source)


def builtin_compose(vm):
    """( block1 block2 -- combined ) Compose two blocks."""
    from .vm import Block
    block2 = vm.pop()
    block1 = vm.pop()
    combined = Block(block1.tokens + block2.tokens, block1.params)
    vm.push(combined)


def builtin_sutra(vm):
    """( name block -- ) Register a sutra."""
    block = vm.pop()
    name = vm.pop()
    vm.sutras[name] = block


def builtin_smarisu(vm):
    """( name -- ... ) Invoke a sutra by name."""
    name = vm.pop()
    if name not in vm.sutras:
        raise RuntimeError(f"Unknown sutra: {name}")
    vm.execute_quotation(vm.sutras[name])


def builtin_list_sutras(vm):
    """( -- list ) List all registered sutra names."""
    vm.push(list(vm.sutras.keys()))


# === CLI Arguments ===

def builtin_args_count(vm):
    """( -- n ) Push the number of CLI arguments."""
    import sys
    vm.push(len(sys.argv))


def builtin_args_get(vm):
    """( n -- str ) Get the nth CLI argument."""
    import sys
    n = int(vm.pop())
    if 0 <= n < len(sys.argv):
        vm.push(sys.argv[n])
    else:
        vm.push("")


# === File I/O ===

def builtin_read_file(vm):
    """( filename -- contents ) Read file contents."""
    filename = vm.pop()
    with open(filename, 'r', encoding='utf-8') as f:
        vm.push(f.read())


def builtin_write_file(vm):
    """( filename contents -- bool ) Write contents to file."""
    contents = vm.pop()
    filename = vm.pop()
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(str(contents))
        vm.push(True)
    except Exception:
        vm.push(False)


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

    # Math
    'abs': builtin_abs,
    'min': builtin_min,
    'max': builtin_max,
    'pow': builtin_pow,
    'sqrt': builtin_sqrt,
    'floor': builtin_floor,
    'ceil': builtin_ceil,
    'round': builtin_round,

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
    'last': builtin_list_last,
    'reverse': builtin_list_reverse,
    'sort': builtin_list_sort,
    'empty': builtin_list_empty,
    'is-empty': builtin_list_empty,
    'list-concat': builtin_list_concat,
    'take': builtin_list_take,
    'list-drop': builtin_list_drop,
    'list-contains': builtin_list_contains,
    'index-of': builtin_list_index,
    'range': builtin_range,
    'iota': builtin_range_single,

    # String
    ',': builtin_str_concat,
    'concat': builtin_str_concat,
    'split': builtin_str_split,
    'join': builtin_str_join,
    'substring': builtin_str_substring,
    'find': builtin_str_find,
    'replace': builtin_str_replace,
    'trim': builtin_str_trim,
    'upper': builtin_str_upper,
    'lower': builtin_str_lower,
    'starts-with': builtin_str_starts,
    'ends-with': builtin_str_ends,
    'contains': builtin_str_contains,

    # Higher-order
    'map': builtin_map,
    'filter': builtin_filter,
    'fold': builtin_fold,
    'each': builtin_each,
    'times': builtin_times,
    'do': builtin_do,

    # Control flow
    'while': builtin_while,
    'until': builtin_until,
    'loop': builtin_loop,
    'if': builtin_if,
    'if-else': builtin_ifelse,

    # I/O
    'read': builtin_read_line,

    # Type conversion
    'to-string': builtin_to_string,
    'to-int': builtin_to_int,
    'to-float': builtin_to_float,

    # Metaprogramming
    'eval': builtin_eval,
    'code-string': builtin_code_string,
    'compose': builtin_compose,
    'sutra': builtin_sutra,
    'smarisu': builtin_smarisu,
    'list-sutras': builtin_list_sutras,

    # CLI Arguments
    'args-count': builtin_args_count,
    'args-get': builtin_args_get,

    # File I/O
    'read-file': builtin_read_file,
    'write-file': builtin_write_file,
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
