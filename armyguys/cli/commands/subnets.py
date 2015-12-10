# -*- coding: utf-8 -*-

"""Commands for managing subnets."""

import click

from ...jobs import subnets as subnet_jobs

from .. import utils


@click.group()
def subnets():
    """Manage subnets."""
    pass


@subnets.command(name="list")
@click.option(
    "--vpc-id",
    help="A VPC to list subnets in.")
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
def list_subnets(
        vpc_id=None,
        verbose=None,
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """List subnets."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)
    if vpc_id:
        utils.log_heading(verbose, "Fetching subnets in VPC " + vpc_id)
        subnets = subnet_jobs.fetch.get_all_in_vpc(aws_profile, vpc_id)
    else:
        utils.log_heading(verbose, "Fetching subnets")
        subnets = subnet_jobs.fetch.get_all(aws_profile)
    if subnets:
        for subnet in subnets:
            utils.echo(verbose, subnet, "SubnetId")
    else:
        utils.log(verbose, "No subnets.")
