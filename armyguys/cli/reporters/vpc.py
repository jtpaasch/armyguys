# -*- coding: utf-8 -*-

"""Loggers/handlers for VPC activity."""

import pprint

import click

def vpc_id(data, pre="", post=""):
    """Echo a VPC Id to STDOUT.

    data
        The data to echo.

    pre
        A string to prepend to the output.

    post
        A string to append to the output.

    """
    output = None
    if hasattr(data, "get"):
        output = data.get("VpcId")
    if not output:
        output = "No VPC found."
    click.echo(str(pre) + str(output) + str(post))

