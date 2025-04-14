#!/usr/bin/env python3

from enum import Enum
from types import MappingProxyType

class Severity(Enum):
    COOL     = 1
    INFO     = 2
    WARN     = 3
    FATAL    = 4

class Colors():
    _COLORS = {
        "NONE": "",
        "RESET": "\033[0m",
        "GREEN": "\033[92m",
        "YELLOW": "\033[93m",
        "RED": "\033[91m"
    }

    COLORS = MappingProxyType(_COLORS)

    @classmethod
    def getCode(cls, name):
        if name not in cls.COLORS:
            return None
        return cls.COLORS[name]

class Styles(Enum):
    PLAIN   = 0
    COLORS  = 1
    ICONS   = 2

SeverityInfo = {
        Severity.COOL:     {"icon": "🚀", "label": "[INFO] ",    "color": "GREEN"},
        Severity.INFO:     {"icon": "✅", "label": "[INFO] ",    "color": "NONE"},
        Severity.WARN:     {"icon": "⚠️", "label": "[WARNING] ", "color": "YELLOW"},
        Severity.FATAL:    {"icon": "❌", "label": "[FATAL] ",   "color": "RED"}
    }

class Messages():
    defaults = {
        "severity_level": Severity.INFO,
        "style": Styles.ICONS
    }

    def print_message(self, message, severity_level, style):
        if style == Styles.PLAIN:
            print(message)
        elif style == Styles.COLORS:
            color_start = Colors.getCode(SeverityInfo[severity_level]["color"])
            color_end = Colors.getCode("RESET")
            print(color_start + message + color_end)
        elif style == Styles.ICONS:
            print(SeverityInfo[severity_level]["icon"] + " " + message)

    def show_message(
            self,
            message,
            severity_level = None,
            style = None
        ):
        # set defaults
        if severity_level is None:
            severity_level = self.defaults["severity_level"]
        if style is None:
            style = self.defaults["style"]
        # If severity_level is not declared in Severity, something is wrong,
        # so we emit a warning.
        # But we don't return, because we might still be able to print the
        # original message.
        if not isinstance(severity_level, Severity):
            print(f"⚠️ Undeclared severity level: {severity_level}")
        # If severity_level is not in SecurityInfo, we print a warning
        # and then we print the message as is.
        # This might mean that we have two warnings, which is intended.
        if severity_level not in SeverityInfo:
            print(f"⚠️ Unhandled severity level: {severity_level}")
            print(message)
            return False
        else:
            # The message should be properly handled based on its security_level
            self.print_message(message, severity_level, style)
            return True
