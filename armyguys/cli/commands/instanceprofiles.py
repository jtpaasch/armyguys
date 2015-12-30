# -*- coding: utf-8 -*-

"""Commands for managing IAM instance profiles."""

import click

from ...jobs import instanceprofiles as instanceprofile_jobs

from ...jobs.exceptions import AwsError
from ...jobs.exceptions import FileDoesNotExist
from ...jobs.exceptions import MissingKey
from ...jobs.exceptions import Non200Response
from ...jobs.exceptions import PermissionDenied
from ...jobs.exceptions import ResourceAlreadyExists
from ...jobs.exceptions import ResourceDoesNotExist
from ...jobs.exceptions import ResourceNotCreated
from ...jobs.exceptions import ResourceNotDeleted

from .. import utils


@click.group()
def instanceprofiles():
    """Manage IAM instance profiles."""
    pass


@instanceprofiles.command(name="list")
@click.option(
    "--profile",
    help="An AWS profile to connect with.")
@click.option(
    "--access-key-id",
    help="An AWS access key ID.")
@click.option(
    "--access-key-secret",
    help="An AWS access key secret.")
def list_instance_profiles(
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """List IAM instance profiles."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)

    try:
        records = instanceprofile_jobs.fetch_all(aws_profile)
    except PermissionDenied:
        msg = "You don't have permission to view instance profiles."
        raise click.ClickException(msg)
    except (MissingKey, Non200Response) as error:
        raise click.ClickException(str(error))
    except AwsError as error:
        raise click.ClickException(str(error))
    except ResourceDoesNotExist as error:
        raise click.ClickException(str(error))

    if records:
        for record in records:
            display_name = instanceprofile_jobs.get_display_name(record)
            click.echo(display_name)


@instanceprofiles.command(name="create")
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
def create_instance_profile(
        name,
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """Create IAM instance profiles."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)

    try:
        records = instanceprofile_jobs.create(aws_profile, name)
    except PermissionDenied:
        msg = "You don't have permission to create IAM instance profiles."
        raise click.ClickException(msg)
    except (MissingKey, Non200Response) as error:
        raise click.ClickException(str(error))
    except AwsError as error:
        raise click.ClickException(str(error))
    except (ResourceDoesNotExist, ResourceAlreadyExists, ResourceNotCreated, FileDoesNotExist) as error:
        raise click.ClickException(str(error))

    if records:
        for record in records:
            display_name = instanceprofile_jobs.get_display_name(record)
            click.echo(display_name)


@instanceprofiles.command(name="delete")
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
def delete_role(
        name,
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """Delete IAM instance profiles."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)

    try:
        instanceprofile_jobs.delete(aws_profile, name)
    except PermissionDenied:
        msg = "You don't have permission to delete instance profiles."
        raise click.ClickException(msg)
    except (MissingKey, Non200Response) as error:
        raise click.ClickException(str(error))
    except AwsError as error:
        raise click.ClickException(str(error))
    except (ResourceDoesNotExist, ResourceNotDeleted) as error:
        raise click.ClickException(str(error))


@instanceprofiles.command(name="attach")
@click.argument("instance_profile")
@click.argument("role")
@click.option(
    "--profile",
    help="An AWS profile to connect with.")
@click.option(
    "--access-key-id",
    help="An AWS access key ID.")
@click.option(
    "--access-key-secret",
    help="An AWS access key secret.")
def attach_role(
        instance_profile,
        role,
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """Attach roles to instance profiles."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)

    try:
        instanceprofile_jobs.attach(aws_profile, instance_profile, role)
    except PermissionDenied:
        msg = "You don't have permission to attach roles."
        raise click.ClickException(msg)
    except (MissingKey, Non200Response) as error:
        raise click.ClickException(str(error))
    except AwsError as error:
        raise click.ClickException(str(error))
    except (ResourceDoesNotExist, ResourceNotDeleted) as error:
        raise click.ClickException(str(error))


@instanceprofiles.command(name="detach")
@click.argument("instance_profile")
@click.argument("role")
@click.option(
    "--profile",
    help="An AWS profile to connect with.")
@click.option(
    "--access-key-id",
    help="An AWS access key ID.")
@click.option(
    "--access-key-secret",
    help="An AWS access key secret.")
def detach_role(
        instance_profile,
        role,
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """Detach roles from instance profiles."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)

    try:
        instanceprofile_jobs.detach(aws_profile, instance_profile, role)
    except PermissionDenied:
        msg = "You don't have permission to detach roles."
        raise click.ClickException(msg)
    except (MissingKey, Non200Response) as error:
        raise click.ClickException(str(error))
    except AwsError as error:
        raise click.ClickException(str(error))
    except (ResourceDoesNotExist, ResourceNotDeleted) as error:
        raise click.ClickException(str(error))
