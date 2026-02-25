# -*- coding: utf-8 -*-
"""
Kapila C Code Generator
=======================

Generates C code from Kapila AST.

The generated code uses the Kapila runtime library (runtime/kapila.h).
Blocks/quotations become static C functions with KBlock (void(*)(void)) signatures.
Higher-order operations (map, filter, fold, each, times, while, until, if, if-else, do)
emit calls passing block function pointers.
Variables use var_set/var_get from the runtime.
"""

from typing import List, Dict, Optional
from ..parser.ast import (
    Node, Expr, Stmt, Program,
    NumberLit, StringLit, BoolLit, Word, QuotedWord,
    Block, ListLit, MapLit,
    BinaryExpr, UnaryExpr, Conditional, PostfixAction,
    WordDef, VarAssign, ExprStmt,
    NodeVisitor
)
from ..vocabulary import VOCABULARY


class CGenerator(NodeVisitor):
    """Generates C code from Kapila AST."""

    def __init__(self):
        self.output: List[str] = []
        self.indent_level = 0
        self.word_defs: Dict[str, WordDef] = {}
        self.variables: set = set()
        self.block_counter = 0
        self.block_defs: List[str] = []  # generated block function source
        self._build_builtin_map()

    def _build_builtin_map(self):
        """Build a complete mapping from word names to C runtime calls."""
        # Direct C runtime function calls for simple (non-higher-order) builtins
        self.simple_builtins = {
            # Arithmetic
            '+': 'add_op', '-': 'sub_op', '*': 'mul_op', '/': 'div_op', '%': 'mod_op',

            # Math
            'abs': 'abs_op', 'min': 'min_op', 'max': 'max_op',
            'pow': 'pow_op', 'sqrt': 'sqrt_op',
            'floor': 'floor_op', 'ceil': 'ceil_op', 'round': 'round_op',

            # Comparison
            '<': 'lt_op', '>': 'gt_op', '=': 'eq_op',
            '!=': 'neq_op', '<=': 'lte_op', '>=': 'gte_op',

            # Logic
            'and': 'and_op', 'or': 'or_op', 'not': 'not_op',

            # Stack
            'dup': 'dup_op', 'drop': 'drop_op', 'swap': 'swap_op',
            'over': 'over_op', 'rot': 'rot_op',

            # I/O
            'print': 'println_op', 'println': 'println_op',
            'read': 'read_line_op',
            'read-file': 'file_read_op', 'write-file': 'file_write_op',

            # String
            'length': 'list_len_op',
            'concat': 'str_concat_op', ',': 'str_concat_op',
            'split': 'str_split_op',
            'join': 'str_join_op',
            'substring': 'str_substring_op',
            'find': 'str_find_op',
            'replace': 'str_replace_op',
            'trim': 'str_trim_op',
            'upper': 'str_upper_op',
            'lower': 'str_lower_op',
            'starts-with': 'str_starts_with_op',
            'ends-with': 'str_ends_with_op',
            'contains': 'str_contains_op',

            # List
            'nth': 'list_at_op',
            'append': 'list_push_op',
            'first': 'list_first_op',
            'rest': 'list_rest_op',
            'last': 'list_last_op',
            'reverse': 'list_reverse_op',
            'sort': 'list_sort_op',
            'is-empty': 'list_is_empty_op', 'empty': 'list_is_empty_op',
            'list-concat': 'list_concat_op',
            'take': 'list_take_op',
            'list-drop': 'list_drop_items_op',
            'list-contains': 'list_contains_op',
            'index-of': 'list_index_of_op',
            'range': 'range_op',
            'iota': 'iota_op',

            # Type conversion
            'to-string': 'to_string_op',
            'to-int': 'to_int_op',
            'to-float': 'to_float_op',

            # CLI arguments
            'args-count': 'args_count_op',
            'args-get': 'args_get_op',
        }

        # Higher-order words that need block arguments
        # These are handled specially in visit_Word based on what's on the stack
        self.higher_order_words = {
            'map', 'filter', 'fold', 'each', 'times',
            'while', 'until',
            'if', 'if-else',
            'do',
        }

        # Add all Kannada vocabulary mappings
        for kannada, english in VOCABULARY.items():
            if english in self.simple_builtins:
                self.simple_builtins[kannada] = self.simple_builtins[english]
            elif english in self.higher_order_words:
                self.higher_order_words.add(kannada)

        # Boolean literals
        self.bool_literals = {
            'true': True, 'false': False,
            'ನಿಜ': True, 'ಸುಳ್ಳು': False,
            'ಸರಿ': True, 'ತಪ್ಪು': False,
            'ಹೌದು': True, 'ಇಲ್ಲ': False,
            'ಬೇಸ': False,
        }

        # Map Kannada higher-order words to their English equivalent
        self._ho_english = {}
        for kannada, english in VOCABULARY.items():
            if english in self.higher_order_words:
                self._ho_english[kannada] = english

    def _get_ho_english(self, name: str) -> str:
        """Get the English equivalent of a higher-order word."""
        if name in self._ho_english:
            return self._ho_english[name]
        return name

    def _emit(self, line: str):
        indent = '    ' * self.indent_level
        self.output.append(indent + line)

    def _emit_header(self):
        self._emit('/* Generated by Kapila Compiler */')
        self._emit('#include "kapila.h"')
        self._emit('')
        self._emit('/* === Block functions === */')
        self._emit('')

    def _get_block_func_name(self, block: Block) -> str:
        """Generate a C function for a block and return its name."""
        func_name = f'_block_{self.block_counter}'
        self.block_counter += 1

        lines = []
        lines.append(f'static void {func_name}(void) {{')

        # Save current state
        saved_output = self.output
        saved_indent = self.indent_level
        self.output = []
        self.indent_level = 1

        # Handle block params: pop from stack into variables
        for param in reversed(block.params):
            self.variables.add(param)
            self._emit(f'var_set("{param}", pop());')

        # Generate body using _visit_body_items for higher-order pattern detection
        self._visit_body_items(block.body)

        body_lines = self.output

        # Restore state
        self.output = saved_output
        self.indent_level = saved_indent

        for line in body_lines:
            lines.append(line)
        lines.append('}')

        self.block_defs.append('\n'.join(lines))
        return func_name

    def _mangle_name(self, name: str) -> str:
        result = []
        for ch in name:
            if ch.isalnum() or ch == '_':
                result.append(ch)
            else:
                result.append(f'_{ord(ch):x}_')
        mangled = ''.join(result)
        if not mangled or mangled[0].isdigit():
            mangled = '_' + mangled
        return 'word_' + mangled

    # === Visitor Methods ===

    def visit_Program(self, node: Program):
        for stmt in node.statements:
            self.visit(stmt)

    def visit_ExprStmt(self, node: ExprStmt):
        self.visit(node.expr)

    def visit_VarAssign(self, node: VarAssign):
        self.visit(node.value)
        self.variables.add(node.name)
        escaped = self._escape_str(node.name)
        self._emit(f'var_set("{escaped}", pop());')

    def visit_WordDef(self, node: WordDef):
        pass  # Handled separately

    def visit_NumberLit(self, node: NumberLit):
        if isinstance(node.value, int):
            self._emit(f'push_int({node.value});')
        else:
            self._emit(f'push_float({node.value});')

    def visit_StringLit(self, node: StringLit):
        escaped = self._escape_str(node.value)
        self._emit(f'push_str("{escaped}");')

    def visit_BoolLit(self, node: BoolLit):
        val = 'true' if node.value else 'false'
        self._emit(f'push_bool({val});')

    def visit_Word(self, node: Word):
        name = node.name

        # Empty word (parser artifact)
        if not name:
            return

        # Boolean literals
        if name in self.bool_literals:
            val = 'true' if self.bool_literals[name] else 'false'
            self._emit(f'push_bool({val});')
            return

        # Variable reference
        if name in self.variables:
            escaped = self._escape_str(name)
            self._emit(f'push_value(var_get("{escaped}"));')
            return

        # User-defined word
        if name in self.word_defs:
            c_name = self._mangle_name(name)
            self._emit(f'{c_name}();')
            return

        # Simple builtin
        if name in self.simple_builtins:
            op = self.simple_builtins[name]
            self._emit(f'{op}();')
            return

        # Higher-order words - check for pending blocks
        if name in self.higher_order_words:
            english = self._get_ho_english(name)
            if hasattr(self, '_pending_blocks') and self._pending_blocks:
                self._emit_higher_order_call(english)
                return
            self._emit(f'/* higher-order word: {name} (no block available) */')
            return

        # Variable in word body - try as variable
        # In word bodies, unknown words used with := might be variables
        self._emit(f'/* unknown word: {name} */')

    def visit_BinaryExpr(self, node: BinaryExpr):
        self.visit(node.left)
        self.visit(node.right)

        ops = {
            '+': 'add_op', '-': 'sub_op', '*': 'mul_op', '/': 'div_op', '%': 'mod_op',
            '<': 'lt_op', '>': 'gt_op', '=': 'eq_op',
            '!=': 'neq_op', '<=': 'lte_op', '>=': 'gte_op',
            'and': 'and_op', 'or': 'or_op',
            'ಮತ್ತು': 'and_op', 'ಅಥವಾ': 'or_op',
        }

        if node.op in ops:
            self._emit(f'{ops[node.op]}();')

    def visit_UnaryExpr(self, node: UnaryExpr):
        self.visit(node.operand)
        if node.op == '-':
            self._emit('{ Value _a = pop(); if (_a.type == VAL_FLOAT) push_float(-_a.f); else push_int(-_a.i); }')
        elif node.op in ('not', 'ಅಲ್ಲ'):
            self._emit('not_op();')

    def visit_PostfixAction(self, node: PostfixAction):
        self.visit(node.value)

        # Process actions, looking for higher-order patterns
        i = 0
        actions = node.actions
        while i < len(actions):
            action = actions[i]
            name = action.name
            english = self._get_ho_english(name)

            if english in self.higher_order_words:
                # Higher-order word: the preceding Block(s) on the codegen stack
                # were already emitted. We need to look backwards in the actions
                # for blocks that were already visited.
                # Actually, in the postfix style, blocks come before the word.
                # They've already been pushed. We just emit the call.
                self._emit(f'/* {name} - handled inline */')
            else:
                self.visit(action)
            i += 1

    def visit_Conditional(self, node: Conditional):
        self.visit(node.condition)
        self._emit('if (pop_bool()) {')
        self.indent_level += 1
        if node.true_block:
            for item in node.true_block.body:
                self.visit(item)
        self.indent_level -= 1
        if node.false_block:
            self._emit('} else {')
            self.indent_level += 1
            for item in node.false_block.body:
                self.visit(item)
            self.indent_level -= 1
        self._emit('}')

    def visit_Block(self, node: Block):
        """Generate a block function and emit the appropriate higher-order call.

        In Kapila, blocks appear before the higher-order word that consumes them.
        The codegen needs to look ahead at the next sibling to determine what
        kind of call to emit. Since we can't always look ahead from here,
        we generate the block function and store it. The consuming word
        (in _emit_block_call) will use it.
        """
        func_name = self._get_block_func_name(node)
        # Store for the next higher-order word to consume
        self._pending_block = getattr(self, '_pending_block', None)
        if not hasattr(self, '_pending_blocks'):
            self._pending_blocks = []
        self._pending_blocks.append(func_name)

    def _consume_block(self) -> Optional[str]:
        """Consume a pending block function name."""
        if hasattr(self, '_pending_blocks') and self._pending_blocks:
            return self._pending_blocks.pop(0)
        return None

    def visit_ListLit(self, node: ListLit):
        self._emit('{')
        self.indent_level += 1
        self._emit('KList* _list = list_new();')
        for elem in node.elements:
            self.visit(elem)
            self._emit('list_push_item(_list, pop());')
        self._emit('push_list(_list);')
        self.indent_level -= 1
        self._emit('}')

    def visit_MapLit(self, node: MapLit):
        self._emit('/* Map literals not yet supported in C codegen */')

    def visit_QuotedWord(self, node: QuotedWord):
        escaped = self._escape_str(node.name)
        self._emit(f'push_str("{escaped}");')

    def _escape_str(self, s: str) -> str:
        """Escape a string for C string literal."""
        return (s.replace('\\', '\\\\')
                 .replace('"', '\\"')
                 .replace('\n', '\\n')
                 .replace('\r', '\\r')
                 .replace('\t', '\\t'))

    def generate(self, program: Program) -> str:
        """Generate C code for a program."""
        # Pre-pass: collect word definitions
        for stmt in program.statements:
            if isinstance(stmt, WordDef):
                self.word_defs[stmt.name] = stmt

        # Pre-pass: collect variables from VarAssign and word body assignments
        self._collect_variables(program)

        # First pass: generate word functions and main body into temp buffers
        # (this also lazily generates block functions as they're encountered)
        saved_output = self.output
        self.output = []

        # Generate word functions into temp buffer
        word_code = []
        for name, word_def in self.word_defs.items():
            self._generate_word_function(name, word_def)
        word_code = self.output

        # Generate main body into temp buffer
        self.output = []
        main_body = []
        self.indent_level = 1
        for stmt in program.statements:
            if not isinstance(stmt, WordDef):
                self._visit_stmt_with_ho(stmt)
        main_body = self.output
        self.indent_level = 0

        # Now assemble final output
        self.output = saved_output

        # Header
        self._emit_header()

        # Block function forward declarations
        for block_def in self.block_defs:
            self.output.append(block_def)
            self.output.append('')

        # Word function forward declarations
        for name in self.word_defs:
            c_name = self._mangle_name(name)
            self.output.append(f'void {c_name}(void);')
        self.output.append('')

        # Word functions
        for line in word_code:
            self.output.append(line)

        # Main function
        self._emit('int main(int argc, char** argv) {')
        self.indent_level += 1
        self._emit('kapila_init_args(argc, argv);')
        self._emit('')

        for line in main_body:
            self.output.append(line)

        self._emit('')
        self._emit('kapila_cleanup();')
        self._emit('return 0;')
        self.indent_level -= 1
        self._emit('}')

        return '\n'.join(self.output)

    def _collect_variables(self, program: Program):
        """Collect variable names from the program."""
        for stmt in program.statements:
            if isinstance(stmt, VarAssign):
                self.variables.add(stmt.name)

    def _visit_stmt_with_ho(self, stmt):
        """Visit a statement, handling higher-order word patterns."""
        if isinstance(stmt, ExprStmt):
            self._visit_expr_ho(stmt.expr)
        elif isinstance(stmt, VarAssign):
            self.visit(stmt)
        else:
            self.visit(stmt)

    def _visit_expr_ho(self, expr):
        """Visit an expression, detecting higher-order patterns.

        Higher-order patterns in postfix:
          list [block] map       -> map_block_op(block_fn)
          list [block] filter    -> filter_block_op(block_fn)
          list init [block] fold -> fold_block_op(block_fn)
          list [block] each      -> each_block_op(block_fn)
          n [block] times        -> times_block_op(block_fn)
          [cond] [body] while    -> while_block_op(cond_fn, body_fn)
          [cond] [body] until    -> until_block_op(cond_fn, body_fn)
          bool [then] if         -> if_block_op(then_fn)
          bool [then] [else] if-else -> ifelse_block_op(then_fn, else_fn)
          [block] do             -> do_block_op(block_fn)

        In PostfixAction nodes, blocks appear as part of the value chain.
        """
        if isinstance(expr, PostfixAction):
            self._visit_postfix_ho(expr)
        else:
            self.visit(expr)

    def _visit_postfix_ho(self, node: PostfixAction):
        """Handle PostfixAction with higher-order word detection."""
        # Visit the value part first
        self.visit(node.value)

        # Process actions
        for action in node.actions:
            name = action.name
            english = self._get_ho_english(name)

            if english in self.higher_order_words and hasattr(self, '_pending_blocks') and self._pending_blocks:
                self._emit_higher_order_call(english)
            else:
                self.visit(action)

    def _emit_higher_order_call(self, english_name: str):
        """Emit C code for a higher-order operation."""
        if english_name == 'do':
            fn = self._consume_block()
            if fn:
                self._emit(f'do_block_op({fn});')

        elif english_name in ('map', 'filter', 'each'):
            fn = self._consume_block()
            if fn:
                self._emit(f'{english_name}_block_op({fn});')

        elif english_name == 'fold':
            fn = self._consume_block()
            if fn:
                self._emit(f'fold_block_op({fn});')

        elif english_name == 'times':
            fn = self._consume_block()
            if fn:
                self._emit(f'times_block_op({fn});')

        elif english_name == 'while':
            # Two blocks: first = cond, second = body
            first = self._consume_block()
            second = self._consume_block()
            if first and second:
                self._emit(f'while_block_op({first}, {second});')
            elif first:
                self._emit(f'do_block_op({first});')

        elif english_name == 'until':
            first = self._consume_block()
            second = self._consume_block()
            if first and second:
                self._emit(f'until_block_op({first}, {second});')
            elif first:
                self._emit(f'do_block_op({first});')

        elif english_name == 'if':
            fn = self._consume_block()
            if fn:
                self._emit(f'if_block_op({fn});')

        elif english_name == 'if-else':
            # Two blocks: first = then, second = else
            then_fn = self._consume_block()
            else_fn = self._consume_block()
            if then_fn and else_fn:
                self._emit(f'ifelse_block_op({then_fn}, {else_fn});')

    def _generate_word_function(self, name: str, word_def: WordDef):
        """Generate C function for a word definition.

        Word bodies use postfix notation. We need to detect higher-order
        patterns: sequences of blocks followed by map/filter/fold/etc.
        """
        c_name = self._mangle_name(name)
        self._emit(f'void {c_name}(void) {{')
        self.indent_level += 1

        self._visit_body_items(word_def.body)

        self.indent_level -= 1
        self._emit('}')
        self._emit('')

    def _visit_body_items(self, items):
        """Visit a sequence of body items, detecting higher-order patterns."""
        i = 0
        while i < len(items):
            item = items[i]

            # Handle VarAssign nodes (from parser)
            if isinstance(item, VarAssign):
                self.visit(item)
                i += 1
                continue

            # Look for Block followed by higher-order word
            if isinstance(item, Block):
                # Collect consecutive blocks
                blocks = []
                while i < len(items) and isinstance(items[i], Block):
                    func_name = self._get_block_func_name(items[i])
                    blocks.append(func_name)
                    i += 1

                # Check if next item is a higher-order word
                if i < len(items) and isinstance(items[i], Word):
                    name = items[i].name
                    english = self._get_ho_english(name)
                    if english in self.higher_order_words:
                        self._emit_ho_from_blocks(english, blocks)
                        i += 1
                        continue

                # Not followed by higher-order word - just push blocks as pending
                for b in blocks:
                    if not hasattr(self, '_pending_blocks'):
                        self._pending_blocks = []
                    self._pending_blocks.append(b)
                continue

            # Check for VarAssign pattern in body: value name :=
            # (for older parser output that may produce Word nodes)
            if (isinstance(item, Word) and
                i + 1 < len(items) and
                isinstance(items[i + 1], Word) and
                items[i + 1].name == ':='):
                var_name = item.name
                self.variables.add(var_name)
                escaped = self._escape_str(var_name)
                self._emit(f'var_set("{escaped}", pop());')
                i += 2
                continue

            # Normal item
            if isinstance(item, Word):
                name = item.name
                english = self._get_ho_english(name)
                if english in self.higher_order_words and hasattr(self, '_pending_blocks') and self._pending_blocks:
                    self._emit_higher_order_call(english)
                    i += 1
                    continue

            self.visit(item)
            i += 1

    def _emit_ho_from_blocks(self, english_name: str, blocks: List[str]):
        """Emit a higher-order call given pre-collected block function names."""
        if english_name == 'do' and len(blocks) >= 1:
            self._emit(f'do_block_op({blocks[-1]});')

        elif english_name in ('map', 'filter', 'each') and len(blocks) >= 1:
            self._emit(f'{english_name}_block_op({blocks[-1]});')

        elif english_name == 'fold' and len(blocks) >= 1:
            self._emit(f'fold_block_op({blocks[-1]});')

        elif english_name == 'times' and len(blocks) >= 1:
            self._emit(f'times_block_op({blocks[-1]});')

        elif english_name == 'while' and len(blocks) >= 2:
            self._emit(f'while_block_op({blocks[0]}, {blocks[1]});')
        elif english_name == 'while' and len(blocks) == 1:
            self._emit(f'do_block_op({blocks[0]});')

        elif english_name == 'until' and len(blocks) >= 2:
            self._emit(f'until_block_op({blocks[0]}, {blocks[1]});')
        elif english_name == 'until' and len(blocks) == 1:
            self._emit(f'do_block_op({blocks[0]});')

        elif english_name == 'if' and len(blocks) >= 1:
            self._emit(f'if_block_op({blocks[-1]});')

        elif english_name == 'if-else' and len(blocks) >= 2:
            self._emit(f'ifelse_block_op({blocks[-2]}, {blocks[-1]});')


def generate_c(program: Program) -> str:
    """Generate C code from a Kapila program."""
    generator = CGenerator()
    return generator.generate(program)
