# -*- coding: utf-8 -*-

"""Commands for managing availability zones."""

import click

from ...jobs import vpcs as vpc_jobs

from ...jobs.exceptions import AwsError
from ...jobs.exceptions import MissingKey
from ...jobs.exceptions import Non200Response
from ...jobs.exceptions import PermissionDenied

from .. import utils


@click.group()
def vpcs():
    """Manage VPCs."""
    pass


@vpcs.command(name="list")
@click.option(
    "--profile",
    help="An AWS profile to connect with.")
@click.option(
    "--access-key-id",
    help="An AWS access key ID.")
@click.option(
    "--access-key-secret",
    help="An AWS access key secret.")
def list_vpcs(
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """List VPCs."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)

    try:
        vpcs = vpc_jobs.fetch_all(aws_profile)
    except PermissionDenied:
        msg = "You don't have permission to view VPCs."
        raise click.ClickException(msg)
    except (MissingKey, Non200Response) as error:
        raise click.ClickException(str(error))
    except AwsError as error:
        raise click.ClickException(str(error))

    if vpcs:
        for vpc in vpcs:
            display_name = vpc_jobs.get_display_name(vpc)
            click.echo(display_name)
