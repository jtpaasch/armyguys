# -*- coding: utf-8 -*-

"""Commands for managing IAM roles."""

import click

from ...jobs import roles as role_jobs

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
def roles():
    """Manage IAM roles."""
    pass


@roles.command(name="list")
@click.option(
    "--profile",
    help="An AWS profile to connect with.")
@click.option(
    "--access-key-id",
    help="An AWS access key ID.")
@click.option(
    "--access-key-secret",
    help="An AWS access key secret.")
def list_roles(
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """List IAM roles."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)

    try:
        records = role_jobs.fetch_all(aws_profile)
    except PermissionDenied:
        msg = "You don't have permission to view roles."
        raise click.ClickException(msg)
    except (MissingKey, Non200Response) as error:
        raise click.ClickException(str(error))
    except AwsError as error:
        raise click.ClickException(str(error))
    except ResourceDoesNotExist as error:
        raise click.ClickException(str(error))

    if records:
        for record in records:
            display_name = role_jobs.get_display_name(record)
            click.echo(display_name)

@roles.command(name="create")
@click.argument("name")
@click.option(
    "--filepath",
    type=click.Path(exists=True),
    help="A file containing the role definition.")
@click.option(
    "--contents",
    help="A JSON string of the role definition.")
@click.option(
    "--profile",
    help="An AWS profile to connect with.")
@click.option(
    "--access-key-id",
    help="An AWS access key ID.")
@click.option(
    "--access-key-secret",
    help="An AWS access key secret.")
def create_role(
        name,
        filepath=None,
        contents=None,
        private=None,
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """Create IAM roles."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)

    required_params = [filepath, contents]
    if not any(required_params):
        msg = "Which filepath or contents? Use --filepath or --contents."
        raise click.ClickException(msg)
    elif any(required_params) and all(required_params):
        msg = "Specify a filepath or contents, but not both."
        raise click.ClickException(msg)
    
    try:
        records = role_jobs.create(aws_profile, name, filepath, contents)
    except PermissionDenied:
        msg = "You don't have permission to create IAM roles."
        raise click.ClickException(msg)
    except (MissingKey, Non200Response) as error:
        raise click.ClickException(str(error))
    except AwsError as error:
        raise click.ClickException(str(error))
    except (ResourceDoesNotExist, ResourceAlreadyExists, ResourceNotCreated, FileDoesNotExist) as error:
        raise click.ClickException(str(error))

    if records:
        for record in records:
            display_name = role_jobs.get_display_name(record)
            click.echo(display_name)


@roles.command(name="delete")
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
    """Delete IAM roles."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)

    try:
        role_jobs.delete(aws_profile, name)
    except PermissionDenied:
        msg = "You don't have permission to delete roles."
        raise click.ClickException(msg)
    except (MissingKey, Non200Response) as error:
        raise click.ClickException(str(error))
    except AwsError as error:
        raise click.ClickException(str(error))
    except (ResourceDoesNotExist, ResourceNotDeleted) as error:
        raise click.ClickException(str(error))
