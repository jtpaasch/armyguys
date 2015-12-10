# -*- coding: utf-8 -*-

"""Commands for managing VPCs."""

import click

from ...jobs import vpcs as vpc_jobs

from .. import utils


@click.group()
def vpcs():
    """Manage VPCs."""
    pass


@vpcs.command(name="list")
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
def list_vpcs(
        verbose=None,
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """List VPCs."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)
    utils.log_heading(verbose, "Fetching VPCs")
    vpcs = vpc_jobs.fetch.get_all(aws_profile)
    if vpcs:
        for record in vpcs:
            if record["IsDefault"]:
                utils.echo(verbose, record, "VpcId", pre="*")
            else:
                utils.echo(verbose, record, "VpcId")
    else:
        utils.log(verbose, "No VPCs.")
