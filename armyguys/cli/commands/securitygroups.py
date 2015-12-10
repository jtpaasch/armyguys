# -*- coding: utf-8 -*-

"""Commands for managing security groups."""

import click

from ...jobs import securitygroups as sg_jobs

from .. import utils


@click.group()
def securitygroups():
    """Manage security groups."""
    pass


@securitygroups.command(name="list")
@click.option(
    "--vpc-id",
    help="A VPC to list security groups in.")
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
def list_security_groups(
        vpc_id=None,
        verbose=None,
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """List security groups."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)
    if vpc_id:
        utils.log_heading(verbose, "Fetching security groups for " + vpc_id)
        sgs = sg_jobs.fetch.get_all_in_vpc(aws_profile, vpc_id)
    else:
        utils.log_heading(verbose, "Fetching security groups")
        sgs = sg_jobs.fetch.get_all(aws_profile)
    if sgs:
        for sg in sgs:
            utils.echo(verbose, sg, "GroupId")
    else:
        utils.log(verbose, "No security groups.")
