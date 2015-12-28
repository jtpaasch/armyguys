# -*- coding: utf-8 -*-

"""Commands for managing ECS task definitions."""

import click

from ...jobs import taskdefinitions as taskdef_jobs

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
def taskdefinitions():
    """Manage ECS task definitions."""
    pass


@taskdefinitions.command(name="list")
@click.option(
    "--profile",
    help="An AWS profile to connect with.")
@click.option(
    "--access-key-id",
    help="An AWS access key ID.")
@click.option(
    "--access-key-secret",
    help="An AWS access key secret.")
def list_task_definitions(
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """List ECS task definitions."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)

    try:
        records = taskdef_jobs.fetch_all(aws_profile)
    except PermissionDenied:
        msg = "You don't have permission to view task definitions."
        raise click.ClickException(msg)
    except (MissingKey, Non200Response) as error:
        raise click.ClickException(str(error))
    except AwsError as error:
        raise click.ClickException(str(error))
    except ResourceDoesNotExist as error:
        raise click.ClickException(str(error))

    if records:
        for record in records:
            display_name = taskdef_jobs.get_display_name_from_arn(record)
            click.echo(display_name)


@taskdefinitions.command(name="create")
@click.option(
    "--filepath",
    type=click.Path(exists=True),
    help="A task definition file.")
@click.option(
    "--contents",
    help="A JSON string of the contents.")
@click.option(
    "--profile",
    help="An AWS profile to connect with.")
@click.option(
    "--access-key-id",
    help="An AWS access key ID.")
@click.option(
    "--access-key-secret",
    help="An AWS access key secret.")
def create_task_definition(
        filepath=None,
        contents=None,
        private=None,
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """Create ECS task definitions."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)

    required_params = [filepath, contents]
    if not any(required_params):
        msg = "Which filepath or contents? Use --filepath or --contents."
        raise click.ClickException(msg)
    elif any(required_params) and all(required_params):
        msg = "Specify a filepath or contents, but not both."
        raise click.ClickException(msg)
    
    try:
        record = taskdef_jobs.create(aws_profile, filepath, contents)
    except PermissionDenied:
        msg = "You don't have permission to create task definitions."
        raise click.ClickException(msg)
    except (MissingKey, Non200Response) as error:
        raise click.ClickException(str(error))
    except AwsError as error:
        raise click.ClickException(str(error))
    except (ResourceDoesNotExist, ResourceAlreadyExists, ResourceNotCreated) as error:
        raise click.ClickException(str(error))

    if record:
        display_name = taskdef_jobs.get_display_name(record)
        click.echo(display_name)


@taskdefinitions.command(name="delete")
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
def delete_task_definition(
        name,
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """Delete ECS task definitions."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)

    try:
        taskdef_jobs.delete(aws_profile, name)
    except PermissionDenied:
        msg = "You don't have permission to delete task definitions."
        raise click.ClickException(msg)
    except (MissingKey, Non200Response) as error:
        raise click.ClickException(str(error))
    except AwsError as error:
        raise click.ClickException(str(error))
    except (ResourceDoesNotExist, ResourceAlreadyExists, ResourceNotDeleted) as error:
        raise click.ClickException(str(error))
