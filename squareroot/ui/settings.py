"""Tiny local settings persistence for the SquareRoot UI.

Currently stores only the chosen language. Any failure to read or write
(missing/unwritable home directory, corrupt file, ...) is swallowed and
falls back to the default -- this is a convenience, not critical state.
"""

import json
import os

from . import i18n

_CONFIG_PATH = os.path.expanduser(os.path.join("~", ".squareroot", "config.json"))


def load_language():
    try:
        with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        language = data["language"]
    except (OSError, ValueError, KeyError, TypeError):
        return i18n.DEFAULT_LANGUAGE
    return language if language in i18n.LANGUAGES else i18n.DEFAULT_LANGUAGE


def save_language(language):
    try:
        os.makedirs(os.path.dirname(_CONFIG_PATH), exist_ok=True)
        with open(_CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump({"language": language}, f)
    except OSError:
        pass
