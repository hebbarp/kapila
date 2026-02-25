# -*- coding: utf-8 -*-
"""
Kapila Code Generation
======================

Generates code from Kapila AST.
Supports C backend (default) and optional LLVM IR backend.
"""

from .c_generator import CGenerator, generate_c

# LLVM backend is optional - only import if llvmlite is installed
try:
    from .llvm_generator import LLVMGenerator, generate_llvm
except ImportError:
    LLVMGenerator = None
    generate_llvm = None
