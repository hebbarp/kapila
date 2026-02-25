# -*- coding: utf-8 -*-
"""
Kapila LLVM Code Generator
==========================

Generates LLVM IR from Kapila AST using llvmlite.

The generated code links with the Kapila C runtime library.
"""

from typing import List, Dict, Optional
from llvmlite import ir, binding

from ..parser.ast import (
    Node, Expr, Stmt, Program,
    NumberLit, StringLit, BoolLit, Word, QuotedWord,
    Block, ListLit, MapLit,
    BinaryExpr, UnaryExpr, Conditional, PostfixAction,
    WordDef, VarAssign, ExprStmt,
    NodeVisitor
)


class LLVMGenerator(NodeVisitor):
    """Generates LLVM IR from Kapila AST."""

    def __init__(self):
        # Create module
        self.module = ir.Module(name='kapila_program')
        self.module.triple = binding.get_default_triple()

        # Types
        self.void_type = ir.VoidType()
        self.i8_type = ir.IntType(8)
        self.i32_type = ir.IntType(32)
        self.i64_type = ir.IntType(64)
        self.double_type = ir.DoubleType()
        self.bool_type = ir.IntType(1)
        self.i8_ptr_type = ir.PointerType(self.i8_type)

        # Current function and builder
        self.builder: Optional[ir.IRBuilder] = None
        self.current_func: Optional[ir.Function] = None

        # Symbol tables
        self.word_defs: Dict[str, WordDef] = {}
        self.word_funcs: Dict[str, ir.Function] = {}
        self.variables: Dict[str, ir.AllocaInst] = {}
        self.global_strings: Dict[str, ir.GlobalVariable] = {}

        # Runtime functions (declared as external)
        self.runtime_funcs: Dict[str, ir.Function] = {}

        # String counter for unique names
        self.str_counter = 0

    def generate(self, program: Program) -> str:
        """Generate LLVM IR for a program."""
        # Declare runtime functions
        self._declare_runtime_functions()

        # Collect word definitions first
        for stmt in program.statements:
            if isinstance(stmt, WordDef):
                self.word_defs[stmt.name] = stmt

        # Generate word functions
        for name, word_def in self.word_defs.items():
            self._generate_word_function(name, word_def)

        # Generate main function
        self._generate_main(program)

        return str(self.module)

    def _declare_runtime_functions(self):
        """Declare external runtime functions from kapila.c."""
        # void kapila_init(void)
        self._declare_func('kapila_init', self.void_type, [])

        # void kapila_cleanup(void)
        self._declare_func('kapila_cleanup', self.void_type, [])

        # Stack operations
        self._declare_func('push_int', self.void_type, [self.i64_type])
        self._declare_func('push_float', self.void_type, [self.double_type])
        self._declare_func('push_bool', self.void_type, [self.bool_type])
        self._declare_func('push_str', self.void_type, [self.i8_ptr_type])

        # Arithmetic operations
        self._declare_func('add_op', self.void_type, [])
        self._declare_func('sub_op', self.void_type, [])
        self._declare_func('mul_op', self.void_type, [])
        self._declare_func('div_op', self.void_type, [])
        self._declare_func('mod_op', self.void_type, [])

        # Comparison operations
        self._declare_func('lt_op', self.void_type, [])
        self._declare_func('gt_op', self.void_type, [])
        self._declare_func('eq_op', self.void_type, [])
        self._declare_func('neq_op', self.void_type, [])
        self._declare_func('lte_op', self.void_type, [])
        self._declare_func('gte_op', self.void_type, [])

        # Logic operations
        self._declare_func('and_op', self.void_type, [])
        self._declare_func('or_op', self.void_type, [])
        self._declare_func('not_op', self.void_type, [])

        # Stack manipulation
        self._declare_func('dup_op', self.void_type, [])
        self._declare_func('drop_op', self.void_type, [])
        self._declare_func('swap_op', self.void_type, [])
        self._declare_func('over_op', self.void_type, [])
        self._declare_func('rot_op', self.void_type, [])

        # I/O
        self._declare_func('println_op', self.void_type, [])

        # List operations
        self._declare_func('list_len_op', self.void_type, [])
        self._declare_func('list_first_op', self.void_type, [])
        self._declare_func('list_rest_op', self.void_type, [])
        self._declare_func('list_at_op', self.void_type, [])
        self._declare_func('list_push_op', self.void_type, [])

        # Variable operations (for storing/loading values)
        # We use the stack-based approach: pop to store, push to load

    def _declare_func(self, name: str, ret_type, arg_types: List):
        """Declare an external function."""
        func_type = ir.FunctionType(ret_type, arg_types)
        func = ir.Function(self.module, func_type, name=name)
        self.runtime_funcs[name] = func
        return func

    def _mangle_name(self, name: str) -> str:
        """Convert Kannada/special name to valid identifier."""
        result = []
        for ch in name:
            if ch.isalnum() or ch == '_':
                result.append(ch)
            else:
                result.append(f'_{ord(ch):x}_')
        return 'word_' + ''.join(result)

    def _generate_word_function(self, name: str, word_def: WordDef):
        """Generate LLVM function for a word definition."""
        func_name = self._mangle_name(name)
        func_type = ir.FunctionType(self.void_type, [])
        func = ir.Function(self.module, func_type, name=func_name)
        self.word_funcs[name] = func

        block = func.append_basic_block(name='entry')
        self.builder = ir.IRBuilder(block)
        self.current_func = func

        # Generate body
        for item in word_def.body:
            self.visit(item)

        self.builder.ret_void()

    def _generate_main(self, program: Program):
        """Generate main function."""
        # int main(void)
        func_type = ir.FunctionType(self.i32_type, [])
        main_func = ir.Function(self.module, func_type, name='main')

        block = main_func.append_basic_block(name='entry')
        self.builder = ir.IRBuilder(block)
        self.current_func = main_func

        # Call kapila_init
        self.builder.call(self.runtime_funcs['kapila_init'], [])

        # Generate statements
        for stmt in program.statements:
            if not isinstance(stmt, WordDef):
                self.visit(stmt)

        # Call kapila_cleanup
        self.builder.call(self.runtime_funcs['kapila_cleanup'], [])

        # Return 0
        self.builder.ret(ir.Constant(self.i32_type, 0))

    def _create_global_string(self, value: str) -> ir.GlobalVariable:
        """Create a global string constant."""
        if value in self.global_strings:
            return self.global_strings[value]

        # Encode as UTF-8 bytes with null terminator
        encoded = value.encode('utf-8') + b'\x00'
        str_type = ir.ArrayType(self.i8_type, len(encoded))
        str_const = ir.Constant(str_type, bytearray(encoded))

        name = f'.str.{self.str_counter}'
        self.str_counter += 1

        global_str = ir.GlobalVariable(self.module, str_type, name=name)
        global_str.global_constant = True
        global_str.linkage = 'private'
        global_str.initializer = str_const

        self.global_strings[value] = global_str
        return global_str

    def _get_string_ptr(self, global_str: ir.GlobalVariable) -> ir.Value:
        """Get pointer to first character of global string."""
        zero = ir.Constant(self.i32_type, 0)
        return self.builder.gep(global_str, [zero, zero], inbounds=True)

    # === Visitor Methods ===

    def visit_Program(self, node: Program):
        for stmt in node.statements:
            self.visit(stmt)

    def visit_ExprStmt(self, node: ExprStmt):
        self.visit(node.expr)

    def visit_VarAssign(self, node: VarAssign):
        # Generate value (leaves it on stack)
        self.visit(node.value)
        # For now, we just leave it - compiled code doesn't support variables yet
        # This would require extending the runtime

    def visit_WordDef(self, node: WordDef):
        pass  # Handled separately

    def visit_NumberLit(self, node: NumberLit):
        if isinstance(node.value, int):
            val = ir.Constant(self.i64_type, node.value)
            self.builder.call(self.runtime_funcs['push_int'], [val])
        else:
            val = ir.Constant(self.double_type, node.value)
            self.builder.call(self.runtime_funcs['push_float'], [val])

    def visit_StringLit(self, node: StringLit):
        global_str = self._create_global_string(node.value)
        str_ptr = self._get_string_ptr(global_str)
        self.builder.call(self.runtime_funcs['push_str'], [str_ptr])

    def visit_BoolLit(self, node: BoolLit):
        val = ir.Constant(self.bool_type, 1 if node.value else 0)
        self.builder.call(self.runtime_funcs['push_bool'], [val])

    def visit_Word(self, node: Word):
        name = node.name

        # Check if it's a user-defined word
        if name in self.word_funcs:
            self.builder.call(self.word_funcs[name], [])
            return

        # Built-in operations - map to runtime functions
        builtins = {
            # Arithmetic
            '+': 'add_op', '-': 'sub_op', '*': 'mul_op', '/': 'div_op', '%': 'mod_op',
            'ಕೂಡು': 'add_op', 'ಕೂಡಿಸು': 'add_op',
            'ಕಳೆ': 'sub_op',
            'ಗುಣಿಸು': 'mul_op',
            'ಭಾಗಿಸು': 'div_op',
            'ಶೇಷ': 'mod_op',
            # Comparison
            '<': 'lt_op', '>': 'gt_op', '=': 'eq_op',
            '!=': 'neq_op', '<=': 'lte_op', '>=': 'gte_op',
            'ಕಿರಿದು': 'lt_op', 'ಹಿರಿದು': 'gt_op', 'ಸಮ': 'eq_op',
            'ಸಮನಲ್ಲ': 'neq_op',
            # Logic
            'and': 'and_op', 'or': 'or_op', 'not': 'not_op',
            'ಮತ್ತು': 'and_op', 'ಅಥವಾ': 'or_op', 'ಅಲ್ಲ': 'not_op',
            # Stack manipulation
            'dup': 'dup_op', 'drop': 'drop_op', 'swap': 'swap_op',
            'over': 'over_op', 'rot': 'rot_op',
            'ನಕಲು': 'dup_op', 'ಬಿಡು': 'drop_op', 'ಅದಲುಬದಲು': 'swap_op',
            'ಮೇಲೆ': 'over_op', 'ತಿರುಗಿಸು': 'rot_op',
            # I/O
            'print': 'println_op', 'ಮುದ್ರಿಸು': 'println_op',
            # List operations
            'ಉದ್ದ': 'list_len_op', 'length': 'list_len_op',
            'ಮೊದಲ': 'list_first_op', 'first': 'list_first_op',
            'ಉಳಿದ': 'list_rest_op', 'rest': 'list_rest_op',
            'ತೆಗೆ': 'list_at_op', 'nth': 'list_at_op',
            'ಸೇರಿಸು': 'list_push_op', 'append': 'list_push_op',
        }

        # Boolean literals
        bool_literals = {
            'true': True, 'false': False,
            'ನಿಜ': True, 'ಸುಳ್ಳು': False,
            'ಸರಿ': True, 'ತಪ್ಪು': False,
            'ಹೌದು': True, 'ಇಲ್ಲ': False,
            'ಬೇಸ': False,
        }

        if name in bool_literals:
            val = ir.Constant(self.bool_type, 1 if bool_literals[name] else 0)
            self.builder.call(self.runtime_funcs['push_bool'], [val])
        elif name in builtins:
            op = builtins[name]
            if op in self.runtime_funcs:
                self.builder.call(self.runtime_funcs[op], [])
            # else: function not declared, skip

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
            op = ops[node.op]
            if op in self.runtime_funcs:
                self.builder.call(self.runtime_funcs[op], [])

    def visit_UnaryExpr(self, node: UnaryExpr):
        self.visit(node.operand)
        if node.op == '-':
            # Negate: push -1, multiply
            self.builder.call(self.runtime_funcs['push_int'], [ir.Constant(self.i64_type, -1)])
            self.builder.call(self.runtime_funcs['mul_op'], [])
        elif node.op in ('not', 'ಅಲ್ಲ'):
            self.builder.call(self.runtime_funcs['not_op'], [])

    def visit_PostfixAction(self, node: PostfixAction):
        self.visit(node.value)
        for action in node.actions:
            self.visit(action)

    def visit_Conditional(self, node: Conditional):
        # For conditionals, we need pop_bool from runtime
        # For now, generate inline if using runtime
        # This is a simplified version - full implementation would need pop_bool
        self.visit(node.condition)

        # Create basic blocks
        then_bb = self.current_func.append_basic_block('then')
        else_bb = self.current_func.append_basic_block('else') if node.false_block else None
        merge_bb = self.current_func.append_basic_block('merge')

        # For now, we skip conditional generation - would need pop() to get condition value
        # Just generate then block unconditionally as placeholder
        self.builder.branch(then_bb)

        # Then block
        self.builder.position_at_end(then_bb)
        self.visit(node.true_block)
        self.builder.branch(merge_bb)

        # Else block
        if else_bb:
            self.builder.position_at_end(else_bb)
            self.visit(node.false_block)
            self.builder.branch(merge_bb)

        # Merge block
        self.builder.position_at_end(merge_bb)

    def visit_Block(self, node: Block):
        for item in node.body:
            self.visit(item)

    def visit_ListLit(self, node: ListLit):
        # Lists require runtime support - for now just push elements
        for elem in node.elements:
            self.visit(elem)

    def visit_MapLit(self, node: MapLit):
        pass  # Maps not yet supported

    def visit_QuotedWord(self, node: QuotedWord):
        global_str = self._create_global_string(node.name)
        str_ptr = self._get_string_ptr(global_str)
        self.builder.call(self.runtime_funcs['push_str'], [str_ptr])


def generate_llvm(program: Program) -> str:
    """Generate LLVM IR from a Kapila program."""
    generator = LLVMGenerator()
    return generator.generate(program)
