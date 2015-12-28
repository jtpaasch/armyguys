# -*- coding: utf-8 -*-

"""Commands for managing subnets."""

import click

from ...jobs import subnets as subnet_jobs

from ...jobs.exceptions import AwsError
from ...jobs.exceptions import MissingKey
from ...jobs.exceptions import Non200Response
from ...jobs.exceptions import PermissionDenied
from ...jobs.exceptions import ResourceAlreadyExists
from ...jobs.exceptions import ResourceDoesNotExist
from ...jobs.exceptions import ResourceNotCreated
from ...jobs.exceptions import ResourceNotDeleted

from .. import utils


@click.group()
def subnets() :
    """Manage subnets."""
    pass


@subnets.command(name="list")
@click.option(
    "--vpc",
    help="The name or ID of a VPC.")
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
        profile,
        vpc=None,
        access_key_id=None,
        access_key_secret=None):
    """List subnets."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)

    fetch_func = "fetch_all"
    params = {}
    params["profile"] = aws_profile
    if vpc:
        params["vpc"] = vpc
        fetch_func = "fetch_by_vpc"
    func = getattr(subnet_jobs, fetch_func)
    try:
        records = func(**params)
    except PermissionDenied:
        msg = "You don't have permission to view subnets."
        raise click.ClickException(msg)
    except (MissingKey, Non200Response) as error:
        raise click.ClickException(str(error))
    except ResourceDoesNotExist as error:
        raise click.ClickException(str(error))
    except AwsError as error:
        raise click.ClickException(str(error))

    if records:
        for record in records:
            display_name = subnet_jobs.get_display_name(record)
            click.echo(display_name)

@subnets.command(name="create")
@click.argument("name")
@click.option(
    "--cidr",
    help="The network range, e.g., 10.0.0.0/24.")
@click.option(
    "--vpc",
    help="The name or ID of a VPC.")
@click.option(
    "--zone",
    help="An availability zone.")
@click.option(
    "--tag",
    multiple=True,
    help="KEY:VALUE tag for the subnet.")
@click.option(
    "--profile",
    help="An AWS profile to connect with.")
@click.option(
    "--access-key-id",
    help="An AWS access key ID.")
@click.option(
    "--access-key-secret",
    help="An AWS access key secret.")
def create_subnet(
        name,
        cidr=None,
        vpc=None,
        zone=None,
        tag=None,
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """Create subnets."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)

    if not cidr:
        msg = "Which CIDR? Use --cidr."
        raise click.ClickException(msg)

    if not vpc:
        msg = "Which VPC? Use --vpc."
        raise click.ClickException(msg)

    tags = None
    if tag:
        tags = utils.parse_tags(tag)
    
    try:
        records = subnet_jobs.create(aws_profile, name, vpc, cidr, zone, tags)
    except PermissionDenied:
        msg = "You don't have permission to create subnets."
        raise click.ClickException(msg)
    except (MissingKey, Non200Response) as error:
        raise click.ClickException(str(error))
    except AwsError as error:
        raise click.ClickException(str(error))
    except (ResourceDoesNotExist, ResourceAlreadyExists, ResourceNotCreated) as error:
        raise click.ClickException(str(error))

    if records:
        for record in records:
            display_name = subnet_jobs.get_display_name(record)
            click.echo(display_name)


@subnets.command(name="delete")
@click.argument("name")
@click.option(
    "--profile",
    help="An AWS profile to connect with.")
@click.option(
    "--access-key-id",
    help="An AWS access key ID.")
@click.option(
    "--access-key-secret",
    help="An AWS access key secret.")
def delete_subnet(
        name,
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """Delete subnets."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)

    try:
        records = subnet_jobs.delete(aws_profile, name)
    except PermissionDenied:
        msg = "You don't have permission to delete subnets."
        raise click.ClickException(msg)
    except (MissingKey, Non200Response) as error:
        raise click.ClickException(str(error))
    except AwsError as error:
        raise click.ClickException(str(error))
    except (ResourceDoesNotExist, ResourceNotDeleted) as error:
        raise click.ClickException(str(error))
