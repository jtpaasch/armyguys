# -*- coding: utf-8 -*-

"""Loggers/handlers for auto scaling group activity."""

import pprint

import click

from . import reporting

def name(reports, data):
    """Report the names of one or more auto scaling groups.

    Args:

        reports
            A list of reports to send info to.

        data
            The data to report on.

    """
    if reporting.RECORDS in reports:
        output = pprint.pformat(data)
        click.echo(output)
    else:
        if len(data) > 0:
            for record in data:
                output = record.get("AutoScalingGroupName")
                click.echo(output)
