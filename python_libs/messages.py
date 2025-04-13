#!/usr/bin/env python3

from enum import Enum

class Severity(Enum):
    COOL     = 1
    INFO     = 2
    WARN     = 3
    FATAL    = 4

def show_message(severity_level, message):
    marker = {
        Severity.COOL:     "🚀",
        Severity.INFO:     "✅",
        Severity.WARN:     "⚠️",
        Severity.FATAL:    "❌"
    }
    print(f"{marker[severity_level]} {message}")
