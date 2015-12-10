# -*- coding: utf-8 -*-

"""Loggers/handlers for jobs activity."""

import pprint

import click

from . import reporting

def meta(reports, job):
    """Report a job.

    Args:

        reports
            A list of reports to send info to.

        message
            The job to report.

    """
    if reporting.JOBS in reports:
        click.echo("")
        click.secho(job, bold=True)


def text(reports, message):
    """Report a message.

    Args:

        reports
            A list of reports to send info to.

        message
            The message to report.

    """
    if reporting.JOBS in reports:
        click.echo(message)


def data(reports, data):
    """Report some data.

    Args:

        reports
            A list of reports to send info to.

        data
            The data to report.

    """
    if reporting.JOBS in reports:
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
    if reporting.JOBS in reports:
        click.secho(message, fg="red")


def warning(reports, message):
    """Report a warning message.

    Args:

        reports
            A list of reports to send info to.

        message
            The message to report.

    """
    if reporting.JOBS in reports:
        click.secho(message, fg="yellow")
