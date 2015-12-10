# -*- coding: utf-8 -*-

"""Reporting channels."""

import click


QUIET = 0    # Report only minimal output.
RECORDS = 1  # Report full records.
JOBS = 2     # Report info about jobs.
AWS = 3      # Report AWS responses.


def parse(report):
    """Parse a list of reporting channels.

    Args:

        report
            A list of integers or strings matching
            the constants above.

    Returns:
        The same list, but normalized as integers.

    """
    value_map = {
        "quiet": 0,
        "records": 1,
        "jobs": 2,
        "aws": 3
        }
    valid_values = list(value_map)
    result = []
    for item in report:
        value = None
        try:
            value = value_map[item.lower()]
        except KeyError:
            msg = "Bad --report '" + item + "'. " \
                  + "Must be: " + str(valid_values) + "."
            raise click.ClickException(msg)
        finally:
            result.append(value)
    return result
