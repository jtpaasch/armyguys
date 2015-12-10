# -*- coding: utf-8 -*-

"""Loggers/handlers for jobs activity."""

import pprint

import click

from . import reporting


def emphasize(reports, message):
    """Report a message.

    Args:

        reports
            A list of reports to send info to.

        message
            The message to report.

    """
    click.secho(job, bold=True)


def message(reports, message):
    """Report a message.

    Args:

        reports
            A list of reports to send info to.

        message
            The message to report.

    """
    click.echo(message)


def data(reports, data):
    """Report some data.

    Args:

        reports
            A list of reports to send info to.

        data
            The data to report.

    """
    output = pprint.pformat(data)
    click.echo(output)


def error(reports, message):
    """Report an error message.

    Args:

        reports
            A list of reports to send info to.

        message
            The message to report.

    """
    click.secho(message, fg="red")


def warning(reports, message):
    """Report a warning message.

    Args:

        reports
            A list of reports to send info to.

        message
            The message to report.

    """
    click.secho(message, fg="yellow")
