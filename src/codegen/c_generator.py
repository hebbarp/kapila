# -*- coding: utf-8 -*-
"""
Kapila C Code Generator
=======================

Generates C code from Kapila AST.

The generated code uses a stack-based runtime:
- push_int(n), push_float(f), push_str(s)
- pop_int(), pop_float()
- add(), sub(), mul(), div_op()
- print_top()
"""

from typing import List, Dict
from ..parser.ast import (
    Node, Expr, Stmt, Program,
    NumberLit, StringLit, BoolLit, Word, QuotedWord,
    Block, ListLit, MapLit,
    BinaryExpr, UnaryExpr, Conditional, PostfixAction,
    WordDef, VarAssign, ExprStmt,
    NodeVisitor
)


class CGenerator(NodeVisitor):
    """Generates C code from Kapila AST."""

    def __init__(self):
        self.output: List[str] = []
        self.indent_level = 0
        self.word_defs: Dict[str, WordDef] = {}
        self.variables: Dict[str, str] = {}  # name -> C variable name
        self.var_counter = 0
        self.string_literals: List[str] = []

    def generate(self, program: Program) -> str:
        """Generate C code for a program."""
        # Collect word definitions first
        for stmt in program.statements:
            if isinstance(stmt, WordDef):
                self.word_defs[stmt.name] = stmt

        # Generate header
        self._emit_header()

        # Generate word functions
        for name, word_def in self.word_defs.items():
            self._generate_word_function(name, word_def)

        # Generate main
        self._emit("int main() {")
        self.indent_level += 1
        self._emit("stack_init();")
        self._emit("")

        # Generate statements
        for stmt in program.statements:
            if not isinstance(stmt, WordDef):
                self.visit(stmt)

        self._emit("")
        self._emit("return 0;")
        self.indent_level -= 1
        self._emit("}")

        return "\n".join(self.output)

    def _emit(self, line: str):
        """Emit a line of C code."""
        indent = "    " * self.indent_level
        self.output.append(indent + line)

    def _emit_header(self):
        """Emit C header with runtime."""
        self._emit('#include <stdio.h>')
        self._emit('#include <stdlib.h>')
        self._emit('#include <string.h>')
        self._emit('#include <stdbool.h>')
        self._emit('')
        self._emit('// === Kapila Runtime ===')
        self._emit('')
        self._emit('typedef enum { VAL_INT, VAL_FLOAT, VAL_BOOL, VAL_STR } ValueType;')
        self._emit('')
        self._emit('typedef struct {')
        self._emit('    ValueType type;')
        self._emit('    union {')
        self._emit('        long long i;')
        self._emit('        double f;')
        self._emit('        bool b;')
        self._emit('        char* s;')
        self._emit('    };')
        self._emit('} Value;')
        self._emit('')
        self._emit('#define STACK_SIZE 1024')
        self._emit('Value stack[STACK_SIZE];')
        self._emit('int sp = 0;')
        self._emit('')
        self._emit('void stack_init() { sp = 0; }')
        self._emit('')
        self._emit('void push_int(long long n) {')
        self._emit('    stack[sp].type = VAL_INT;')
        self._emit('    stack[sp].i = n;')
        self._emit('    sp++;')
        self._emit('}')
        self._emit('')
        self._emit('void push_float(double n) {')
        self._emit('    stack[sp].type = VAL_FLOAT;')
        self._emit('    stack[sp].f = n;')
        self._emit('    sp++;')
        self._emit('}')
        self._emit('')
        self._emit('void push_bool(bool b) {')
        self._emit('    stack[sp].type = VAL_BOOL;')
        self._emit('    stack[sp].b = b;')
        self._emit('    sp++;')
        self._emit('}')
        self._emit('')
        self._emit('void push_str(char* s) {')
        self._emit('    stack[sp].type = VAL_STR;')
        self._emit('    stack[sp].s = s;')
        self._emit('    sp++;')
        self._emit('}')
        self._emit('')
        self._emit('Value pop() { return stack[--sp]; }')
        self._emit('Value peek() { return stack[sp-1]; }')
        self._emit('')
        self._emit('// Arithmetic')
        self._emit('void add_op() {')
        self._emit('    Value b = pop(), a = pop();')
        self._emit('    if (a.type == VAL_FLOAT || b.type == VAL_FLOAT)')
        self._emit('        push_float((a.type == VAL_FLOAT ? a.f : a.i) + (b.type == VAL_FLOAT ? b.f : b.i));')
        self._emit('    else push_int(a.i + b.i);')
        self._emit('}')
        self._emit('')
        self._emit('void sub_op() {')
        self._emit('    Value b = pop(), a = pop();')
        self._emit('    if (a.type == VAL_FLOAT || b.type == VAL_FLOAT)')
        self._emit('        push_float((a.type == VAL_FLOAT ? a.f : a.i) - (b.type == VAL_FLOAT ? b.f : b.i));')
        self._emit('    else push_int(a.i - b.i);')
        self._emit('}')
        self._emit('')
        self._emit('void mul_op() {')
        self._emit('    Value b = pop(), a = pop();')
        self._emit('    if (a.type == VAL_FLOAT || b.type == VAL_FLOAT)')
        self._emit('        push_float((a.type == VAL_FLOAT ? a.f : a.i) * (b.type == VAL_FLOAT ? b.f : b.i));')
        self._emit('    else push_int(a.i * b.i);')
        self._emit('}')
        self._emit('')
        self._emit('void div_op() {')
        self._emit('    Value b = pop(), a = pop();')
        self._emit('    double av = a.type == VAL_FLOAT ? a.f : a.i;')
        self._emit('    double bv = b.type == VAL_FLOAT ? b.f : b.i;')
        self._emit('    push_float(av / bv);')
        self._emit('}')
        self._emit('')
        self._emit('void mod_op() {')
        self._emit('    Value b = pop(), a = pop();')
        self._emit('    push_int(a.i % b.i);')
        self._emit('}')
        self._emit('')
        self._emit('// Comparison')
        self._emit('void lt_op() { Value b = pop(), a = pop(); push_bool(a.i < b.i); }')
        self._emit('void gt_op() { Value b = pop(), a = pop(); push_bool(a.i > b.i); }')
        self._emit('void eq_op() { Value b = pop(), a = pop(); push_bool(a.i == b.i); }')
        self._emit('void neq_op() { Value b = pop(), a = pop(); push_bool(a.i != b.i); }')
        self._emit('void lte_op() { Value b = pop(), a = pop(); push_bool(a.i <= b.i); }')
        self._emit('void gte_op() { Value b = pop(), a = pop(); push_bool(a.i >= b.i); }')
        self._emit('')
        self._emit('// Logic')
        self._emit('void and_op() { Value b = pop(), a = pop(); push_bool(a.b && b.b); }')
        self._emit('void or_op() { Value b = pop(), a = pop(); push_bool(a.b || b.b); }')
        self._emit('void not_op() { Value a = pop(); push_bool(!a.b); }')
        self._emit('')
        self._emit('// Stack ops')
        self._emit('void dup_op() { Value a = peek(); stack[sp++] = a; }')
        self._emit('void drop_op() { sp--; }')
        self._emit('void swap_op() { Value b = pop(), a = pop(); stack[sp++] = b; stack[sp++] = a; }')
        self._emit('')
        self._emit('// Print')
        self._emit('void print_op() {')
        self._emit('    Value v = pop();')
        self._emit('    switch(v.type) {')
        self._emit('        case VAL_INT: printf("%lld\\n", v.i); break;')
        self._emit('        case VAL_FLOAT: printf("%g\\n", v.f); break;')
        self._emit('        case VAL_BOOL: printf("%s\\n", v.b ? "ಸರಿ" : "ತಪ್ಪು"); break;')
        self._emit('        case VAL_STR: printf("%s\\n", v.s); break;')
        self._emit('    }')
        self._emit('}')
        self._emit('')
        self._emit('// === Generated Code ===')
        self._emit('')

    def _generate_word_function(self, name: str, word_def: WordDef):
        """Generate C function for a word definition."""
        c_name = self._mangle_name(name)
        self._emit(f'void {c_name}() {{')
        self.indent_level += 1

        for item in word_def.body:
            self.visit(item)

        self.indent_level -= 1
        self._emit('}')
        self._emit('')

    def _mangle_name(self, name: str) -> str:
        """Convert Kannada/special name to valid C identifier."""
        # Replace non-ASCII with hex codes
        result = []
        for ch in name:
            if ch.isalnum() or ch == '_':
                result.append(ch)
            else:
                result.append(f'_{ord(ch):x}_')
        return 'word_' + ''.join(result)

    # === Visitor Methods ===

    def visit_Program(self, node: Program):
        for stmt in node.statements:
            self.visit(stmt)

    def visit_ExprStmt(self, node: ExprStmt):
        self.visit(node.expr)

    def visit_VarAssign(self, node: VarAssign):
        self.visit(node.value)
        c_name = self._mangle_name(node.name)
        self.variables[node.name] = c_name
        self._emit(f'Value {c_name} = pop();')

    def visit_WordDef(self, node: WordDef):
        pass  # Handled separately

    def visit_NumberLit(self, node: NumberLit):
        if isinstance(node.value, int):
            self._emit(f'push_int({node.value});')
        else:
            self._emit(f'push_float({node.value});')

    def visit_StringLit(self, node: StringLit):
        escaped = node.value.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
        self._emit(f'push_str("{escaped}");')

    def visit_BoolLit(self, node: BoolLit):
        val = 'true' if node.value else 'false'
        self._emit(f'push_bool({val});')

    def visit_Word(self, node: Word):
        name = node.name

        # Check if it's a variable
        if name in self.variables:
            c_name = self.variables[name]
            self._emit(f'stack[sp++] = {c_name};')
            return

        # Check if it's a user-defined word
        if name in self.word_defs:
            c_name = self._mangle_name(name)
            self._emit(f'{c_name}();')
            return

        # Built-in operations
        builtins = {
            # Arithmetic
            '+': 'add_op', '-': 'sub_op', '*': 'mul_op', '/': 'div_op', '%': 'mod_op',
            'ಕೂಡು': 'add_op', 'ಕೂಡಿಸು': 'add_op',
            'ಕಳೆ': 'sub_op',
            'ಗುಣಿಸು': 'mul_op',
            'ಭಾಗಿಸು': 'div_op',
            # Comparison
            '<': 'lt_op', '>': 'gt_op', '=': 'eq_op',
            '!=': 'neq_op', '<=': 'lte_op', '>=': 'gte_op',
            'ಕಿರಿದು': 'lt_op', 'ಹಿರಿದು': 'gt_op', 'ಸಮ': 'eq_op',
            # Logic
            'and': 'and_op', 'or': 'or_op', 'not': 'not_op',
            'ಮತ್ತು': 'and_op', 'ಅಥವಾ': 'or_op', 'ಅಲ್ಲ': 'not_op',
            # Stack
            'dup': 'dup_op', 'drop': 'drop_op', 'swap': 'swap_op',
            'ನಕಲು': 'dup_op', 'ಬಿಡು': 'drop_op', 'ಅದಲುಬದಲು': 'swap_op',
            # I/O
            'print': 'print_op', 'ಮುದ್ರಿಸು': 'print_op',
            # Boolean
            'true': 'push_bool(true)', 'false': 'push_bool(false)',
            'ನಿಜ': 'push_bool(true)', 'ಸುಳ್ಳು': 'push_bool(false)',
            'ಸರಿ': 'push_bool(true)', 'ಬೇಸ': 'push_bool(false)',
        }

        if name in builtins:
            op = builtins[name]
            if '(' in op:
                self._emit(f'{op};')
            else:
                self._emit(f'{op}();')
        else:
            self._emit(f'// Unknown word: {name}')

    def visit_BinaryExpr(self, node: BinaryExpr):
        self.visit(node.left)
        self.visit(node.right)

        ops = {
            '+': 'add_op', '-': 'sub_op', '*': 'mul_op', '/': 'div_op', '%': 'mod_op',
            '<': 'lt_op', '>': 'gt_op', '=': 'eq_op',
            '!=': 'neq_op', '<=': 'lte_op', '>=': 'gte_op',
            'ಮತ್ತು': 'and_op', 'and': 'and_op',
            'ಅಥವಾ': 'or_op', 'or': 'or_op',
        }

        if node.op in ops:
            self._emit(f'{ops[node.op]}();')

    def visit_UnaryExpr(self, node: UnaryExpr):
        self.visit(node.operand)
        if node.op == '-':
            self._emit('{ Value a = pop(); push_int(-a.i); }')
        elif node.op in ('not', 'ಅಲ್ಲ'):
            self._emit('not_op();')

    def visit_PostfixAction(self, node: PostfixAction):
        self.visit(node.value)
        for action in node.actions:
            self.visit(action)

    def visit_Conditional(self, node: Conditional):
        self.visit(node.condition)
        self._emit('if (pop().b) {')
        self.indent_level += 1
        self.visit(node.true_block)
        self.indent_level -= 1
        if node.false_block:
            self._emit('} else {')
            self.indent_level += 1
            self.visit(node.false_block)
            self.indent_level -= 1
        self._emit('}')

    def visit_Block(self, node: Block):
        for item in node.body:
            self.visit(item)

    def visit_ListLit(self, node: ListLit):
        self._emit('// List not yet supported in C codegen')

    def visit_MapLit(self, node: MapLit):
        self._emit('// Map not yet supported in C codegen')

    def visit_QuotedWord(self, node: QuotedWord):
        self._emit(f'push_str("{node.name}");')


def generate_c(program: Program) -> str:
    """Generate C code from a Kapila program."""
    generator = CGenerator()
    return generator.generate(program)
