# -*- coding: utf-8 -*-

"""Commands for managing availability zones."""

import click

from ...jobs import availabilityzones as zone_jobs

from .. import utils


@click.group()
def zones():
    """Manage availibility zones."""
    pass


@zones.command(name="list")
@click.option(
    "--verbose",
    type=int,
    default=0,
    multiple=True,
    help="Display details.")
@click.option(
    "--profile",
    help="An AWS profile to connect with.")
@click.option(
    "--access-key-id",
    help="An AWS access key ID.")
@click.option(
    "--access-key-secret",
    help="An AWS access key secret.")
def list_availability_zones(
        verbose=None,
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """List available availability zones."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)
    utils.log_heading(verbose, "Fetching availability zones")
    zones = zone_jobs.fetch.get_all(aws_profile)
    if zones:
        for zone in zones:
            utils.echo(verbose, zone, "ZoneName")
    else:
        utils.log(verbose, "No availability zones.")
