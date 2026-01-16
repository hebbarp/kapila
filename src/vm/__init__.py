# -*- coding: utf-8 -*-
"""
Kapila Virtual Machine
======================

A stack-based virtual machine for executing Kapila code.
"""

from .vm import VM, KapilaError, Block
from .builtins import BUILTINS

__all__ = ['VM', 'KapilaError', 'Block', 'BUILTINS']
