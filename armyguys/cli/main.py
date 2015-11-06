# -*- coding: utf-8 -*-

"""The ``main`` module for the ``cli`` package."""

import click


@click.group()
def cli():
    """Manage AWS resources."""
    pass
