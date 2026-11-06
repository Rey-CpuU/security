"""
Harness Adapters Package for 8-Bit Cyber Operations Office GUI.
"""
from gui.server.harnesses.base import BaseHarnessAdapter
from gui.server.harnesses.claude_code import ClaudeCodeAdapter

__all__ = ["BaseHarnessAdapter", "ClaudeCodeAdapter"]
