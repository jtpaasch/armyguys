# -*- coding: utf-8 -*-

"""Commands for managing availability zones."""

import click

from ...jobs import zones as zone_jobs

from ...jobs.exceptions import AwsError
from ...jobs.exceptions import MissingKey
from ...jobs.exceptions import Non200Response
from ...jobs.exceptions import PermissionDenied

from .. import utils


@click.group()
def zones():
    """Manage availibility zones."""
    pass


@zones.command(name="list")
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
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """List availability zones."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)

    try:
        zones = zone_jobs.fetch_all(aws_profile)
    except PermissionDenied:
        msg = "You don't have premission to view availability zones."
        raise click.ClickException(msg)
    except (MissingKey, Non200Response) as error:
        raise click.ClickException(str(error))
    except AwsError as error:
        raise click.ClickException(str(error))
    
    if zones:
        for zone in zones:
            click.echo(zone["ZoneName"])
