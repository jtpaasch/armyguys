# -*- coding: utf-8 -*-

"""Commands for managing security groups."""

import click

from ...jobs import securitygroups as sg_jobs

from ...jobs.exceptions import AwsError
from ...jobs.exceptions import MissingKey
from ...jobs.exceptions import PermissionDenied
from ...jobs.exceptions import ResourceAlreadyExists
from ...jobs.exceptions import ResourceDoesNotExist
from ...jobs.exceptions import ResourceNotCreated

from .. import utils


@click.group()
def securitygroups():
    """Manage security groups."""
    pass


@securitygroups.command(name="list")
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
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """List security groups."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)

    try:
        security_groups = sg_jobs.fetch_all(aws_profile)
    except PermissionDenied:
        msg = "You don't have premission to view security groups."
        raise click.ClickException(msg)
    except MissingKey as error:
        raise click.ClickException(str(error))
    except AwsError as error:
        raise click.ClickException(str(error))

    if security_groups:
        for security_group in security_groups:
            display_name = sg_jobs.get_display_name(security_group)
            click.echo(display_name)


@securitygroups.command(name="create")
@click.argument("name")
@click.option(
    "--vpc",
    help="A VPC name (or ID).")
@click.option(
    "--profile",
    help="An AWS profile to connect with.")
@click.option(
    "--access-key-id",
    help="An AWS access key ID.")
@click.option(
    "--access-key-secret",
    help="An AWS access key secret.")
def create_security_group(
        name,
        vpc=None,
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """Create security groups."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)

    try:
        security_groups = sg_jobs.create(aws_profile, name, vpc)
    except PermissionDenied:
        msg = "You don't have premission to create security groups."
        raise click.ClickException(msg)
    except (MissingKey, ResourceDoesNotExist, ResourceAlreadyExists, ResourceNotCreated) as error:
        raise click.ClickException(str(error))
    except AwsError as error:
        raise click.ClickException(str(error))

    if security_groups:
        for security_group in security_groups:
            display_name = sg_jobs.get_display_name(security_group)
            click.echo(display_name)
