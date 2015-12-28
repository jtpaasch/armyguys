# -*- coding: utf-8 -*-

"""Commands for managing security groups."""

import click

from ...jobs import securitygroups as sg_jobs

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
        msg = "You don't have permission to view security groups."
        raise click.ClickException(msg)
    except (MissingKey, Non200Response) as error:
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
    "--tag",
    multiple=True,
    help="KEY:VALUE tag for the security group.")
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
        tag=None,
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """Create security groups."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)

    tags = None
    if tag:
        tags = utils.parse_tags(tag)

    try:
        security_groups = sg_jobs.create(aws_profile, name, vpc, tags)
    except PermissionDenied:
        msg = "You don't have permission to create security groups."
        raise click.ClickException(msg)
    except (MissingKey, Non200Response) as error:
        raise click.ClickException(str(error))
    except AwsError as error:
        raise click.ClickException(str(error))
    except (ResourceDoesNotExist, ResourceAlreadyExists, ResourceNotCreated) as error:
        raise click.ClickException(str(error))

    if security_groups:
        for security_group in security_groups:
            display_name = sg_jobs.get_display_name(security_group)
            click.echo(display_name)


@securitygroups.command(name="delete")
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
def delete_security_group(
        name,
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """Delete security groups."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)

    try:
        security_groups = sg_jobs.delete(aws_profile, name)
    except PermissionDenied:
        msg = "You don't have permission to delete security groups."
        raise click.ClickException(msg)
    except (MissingKey, Non200Response) as error:
        raise click.ClickException(str(error))
    except AwsError as error:
        raise click.ClickException(str(error))
    except (ResourceDoesNotExist, ResourceNotDeleted) as error:
        raise click.ClickException(str(error))
