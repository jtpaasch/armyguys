# -*- coding: utf-8 -*-

"""Loggers/handlers for AWS activity."""

import pprint

import click

from . import reporting


def response(reports, data):
    """Echo the data to STDOUT.

    reports
        A list of reports to send info to.

    data
        The data to echo.

    """
    if reporting.AWS in reports:
        output = pprint.pformat(data)
        click.echo(output)
