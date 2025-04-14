#!/usr/bin/env python3

from enum import Enum
from types import MappingProxyType

class Colors():
    _COLORS = {
        # Special values
        "NONE": "",
        "RESET": "\033[0m",
        
        # Regular colors
        "BLACK": "\033[30m",
        "RED": "\033[31m",
        "GREEN": "\033[32m",
        "YELLOW": "\033[33m",
        "BLUE": "\033[34m",
        "MAGENTA": "\033[35m",
        "CYAN": "\033[36m",
        "WHITE": "\033[37m",
        
        # Bright colors
        "BRIGHT_BLACK": "\033[90m",   # Gray
        "BRIGHT_RED": "\033[91m",
        "BRIGHT_GREEN": "\033[92m",
        "BRIGHT_YELLOW": "\033[93m",
        "BRIGHT_BLUE": "\033[94m",
        "BRIGHT_MAGENTA": "\033[95m",
        "BRIGHT_CYAN": "\033[96m",
        "BRIGHT_WHITE": "\033[97m"
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

class Severity():
    _instance_created = False
    levels = {
        'COOL':     {"icon": "🚀", "label": "[INFO] ",    "color": "GREEN"},
        'INFO':     {"icon": "✅", "label": "[INFO] ",    "color": "NONE"},
        'WARN':     {"icon": "⚠️", "label": "[WARNING] ", "color": "YELLOW"},
        'FATAL':    {"icon": "❌", "label": "[FATAL] ",   "color": "RED"}
    }

    def __new__(cls):
        if cls._instance_created:
            raise Exception("Severity is a singleton")

        cls._instance_created = True
        instance = super(Severity, cls).__new__(cls)

        return instance

    def add_level(self, id, icon, label, color):
        self.levels[id] = {"icon": icon, "label": label, "color": color}

    def remove_level(self, id):
        del self.levels[id]

    def set_default_level(self, id = None):
        if id is None:
            Messages.defaults["severity_level"] = None
            return self

        if id not in self.levels:
            raise Exception(f"Severity level does not exist: {id}")

        Messages.defaults["severity_level"] = id
        return self

    def get_default_level(self):
        return Messages.defaults["severity_level"]

class Messages():
    _instance_created = False
    defaults = {
        "severity_level": 'INFO',
        "style": Styles.ICONS
    }

    def __new__(cls):
        if cls._instance_created:
            raise Exception("Severity is a singleton")

        cls._instance_created = True
        instance = super(Messages, cls).__new__(cls)

        return instance

    def __init__(self, severity):
        self.severity = severity

    def print_message(self, message, severity_level, style):
        if style == Styles.PLAIN:
            print(message)
        elif style == Styles.COLORS:
            color_start = Colors.getCode(self.severity.levels[severity_level]["color"])
            color_end = Colors.getCode("RESET")
            print(color_start + message + color_end)
        elif style == Styles.ICONS:
            print(self.severity.levels[severity_level]["icon"] + " " + message)

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
        # If the specified severity_level doesn't exist,
        # we'll print a warning and then we print the message as is.
        if severity_level not in self.severity.levels:
            print(f"⚠️ Undeclared severity level: {severity_level}")
            print(message)
            return False
        else:
            # The message should be properly handled based on its security_level
            self.print_message(message, severity_level, style)
            return True
