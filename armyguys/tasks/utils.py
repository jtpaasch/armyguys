# -*- coding: utf-8 -*-

"""Tools to help with running polarexpress.tasks."""

import os
import pprint
import sys


HELP_OPTION = "--help"
    
TEXT_BOLD = '\033[01m'
TEXT_REVERSE = '\033[07m'
TEXT_DISABLE = '\033[02m'
TEXT_UNDERLINE = '\033[04m'
TEXT_STRIKETHROUGH = '\033[09m'

TEXT_OK = '\033[92m'
TEXT_WARNING = '\033[93m'
TEXT_FAIL = '\033[91m'

TEXT_EMPHASIS = '\033[94m'

TEXT_BG_OK = '\033[42m'
TEXT_BG_WARNING = '\033[43m'
TEXT_BG_FAIL = '\033[41m'

TEXT_RESET = '\033[0m'


def format_for_tty(text, formats):
    """Format text for output to a TTY."""
    pre = "".join(formats) if formats else ""
    post = TEXT_RESET if formats else ""
    return pre + text + post


def echo(text, formats=None):
    """Safely echo output to STDOUT."""
    output = text
    if sys.stdout.isatty():
        output = format_for_tty(text, formats)
    sys.stdout.write(output + os.linesep)


def emphasize(text, formats=[]):
    """Safely echo emphasized text to STDOUT."""
    formats.append(TEXT_EMPHASIS)
    echo(text, formats)


def echo_data(data, formats=None):
    """Safely echo pprinted data to STDOUT."""
    output = pprint.pformat(data)
    echo(output, formats)


def error(text, formats=None):
    """Safely echo error to STDERR, and exit with a status code."""
    if not formats:
        formats = [TEXT_FAIL]
    output = text
    if sys.stderr.isatty():
        output = format_for_tty(text, formats)
    sys.stderr.write(output + os.linesep)


def error_data(data, formats=None):
    """Safely echo pprinted data to STDERR."""
    if not formats:
        formats = [TEXT_WARNING]
    output = pprint.pformat(data)
    error(output, formats)


def exit(code=1):
    """Exit cleanly with a message."""
    if sys.stderr.isatty():
        message = "- Exit code: " + str(code)
        error(message, formats=[TEXT_FAIL])
    sys.exit(code)


def heading(message):
    """Echo a heading message."""
    list_of_chars = ["-"[:] * 72]
    rule = "".join(list_of_chars)
    echo("")
    echo(rule, formats=[TEXT_BOLD])
    echo(message, formats=[TEXT_BOLD])
    echo(rule, formats=[TEXT_BOLD])

