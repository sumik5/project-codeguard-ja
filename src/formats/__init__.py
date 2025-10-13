"""
Formats Package

This package contains all IDE format implementations for rule conversion.

Available Formats:
- CursorFormat: Generates .mdc files for Cursor IDE
- WindsurfFormat: Generates .md files for Windsurf IDE
- CopilotFormat: Generates .instructions.md files for GitHub Copilot

Usage:
    from formats import BaseFormat, ProcessedRule, CursorFormat, WindsurfFormat, CopilotFormat

    version = "1.0.0"
    formats = [
        CursorFormat(version),
        WindsurfFormat(version),
        CopilotFormat(version),
    ]
"""

from formats.base import BaseFormat, ProcessedRule
from formats.cursor import CursorFormat
from formats.windsurf import WindsurfFormat
from formats.copilot import CopilotFormat

__all__ = [
    "BaseFormat",
    "ProcessedRule",
    "CursorFormat",
    "WindsurfFormat",
    "CopilotFormat",
]
