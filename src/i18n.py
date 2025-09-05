import os
import locale
import gettext
import warnings

DOMAIN = "t6modm"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCALES_DIR = os.path.join(BASE_DIR, "locales")

locale.setlocale(locale.LC_ALL, '')
lang_info = locale.getdefaultlocale()
lang = lang_info[0] if lang_info else None
if lang is None:
    warnings.warn('Locale not detected, falling back to "en_US".')
    lang = 'en_US'

translation = gettext.translation(
    DOMAIN,
    localedir=LOCALES_DIR,
    languages=[lang],
    fallback=True
)

_ = translation.gettext