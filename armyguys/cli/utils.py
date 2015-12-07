# -*- coding: utf-8 -*-

"""The ``main`` module for the ``cli`` package."""

import pprint

import click

from ..aws import profile


def get_profile(
        profile_name=None,
        access_key_id=None,
        access_key_secret=None):
    if access_key_id and access_key_secret:
        aws_profile = profile.ephemeral(access_key_id, access_key_secret)
    elif profile_name:
        aws_profile = profile.configured(profile_name)
    else:
        aws_profile = profile.configured()
    return aws_profile


def log(verbose, message):
    if 1 in verbose:
        click.echo(message)


def log_heading(verbose, message):
    if 1 in verbose:
        click.secho(message, bold=True)


def log_emphasis(verbose, message):
    if 1 in verbose:
        click.secho(message, fg="blue")


def log_warning(verbose, message):
    if 1 in verbose:
        click.secho(message, fg="yellow")


def log_error(verbose, message):
    if 1 in verbose:
        click.secho(message, fg="red")


def log_data(verbose, data, key=None, pre="", post=""):
    output = None
    if 2 in verbose:
        output = pprint.pformat(data)
    elif 1 in verbose:
        if key:
            if hasattr(data, "get"):
                output = data.get(key)
            else:
                output = "No key '" + str(key) + "' in " + str(data)
    if output:
        click.echo(pre + output + post)


def echo(verbose, data, key=None, pre="", post=""):
    output = str(data)
    if 2 in verbose:
        output = pprint.pformat(data)
    else:
        if key:
            if hasattr(data, "get"):
                output = data.get(key)
    click.echo(pre + output + post)
