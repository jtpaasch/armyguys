# -*- coding: utf-8 -*-

"""Commands for managing ECS tasks."""

import click

from ...jobs import tasks as task_jobs

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
def tasks():
    """Manage ECS tasks."""
    pass


@tasks.command(name="list")
@click.argument("cluster")
@click.option(
    "--profile",
    help="An AWS profile to connect with.")
@click.option(
    "--access-key-id",
    help="An AWS access key ID.")
@click.option(
    "--access-key-secret",
    help="An AWS access key secret.")
def list_tasks(
        cluster,
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """List ECS tasks."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)

    try:
        records = task_jobs.fetch_all(aws_profile, cluster)
    except PermissionDenied:
        msg = "You don't have permission to view tasks."
        raise click.ClickException(msg)
    except (MissingKey, Non200Response) as error:
        raise click.ClickException(str(error))
    except AwsError as error:
        raise click.ClickException(str(error))
    except ResourceDoesNotExist as error:
        raise click.ClickException(str(error))

    if records:
        for record in records:
            display_name = task_jobs.get_display_name(record)
            click.echo(display_name)


@tasks.command(name="create")
@click.argument("name")
@click.option(
    "--cluster",
    help="A cluster.")
@click.option(
    "--task-definition",
    help="FAMILY:REVISION.")
@click.option(
    "--count",
    type=int,
    help="Number of copies of the task to run.")
@click.option(
    "--profile",
    help="An AWS profile to connect with.")
@click.option(
    "--access-key-id",
    help="An AWS access key ID.")
@click.option(
    "--access-key-secret",
    help="An AWS access key secret.")
def create_task(
        name,
        cluster=None,
        task_definition=None,
        count=None,
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """Create ECS tasks."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)

    if not cluster:
        msg = "Which cluster? Use --cluster."
        raise click.ClickException(msg)
    if not task_definition:
        msg = "Which task definition? Use --task-definition."
        raise click.ClickException(msg)

    try:
        records = task_jobs.create(
            aws_profile,
            name,
            cluster,
            task_definition,
            count)
    except PermissionDenied:
        msg = "You don't have permission to create tasks."
        raise click.ClickException(msg)
    except (MissingKey, Non200Response) as error:
        raise click.ClickException(str(error))
    except AwsError as error:
        raise click.ClickException(str(error))
    except (ResourceDoesNotExist, ResourceAlreadyExists, ResourceNotCreated) as error:
        raise click.ClickException(str(error))

    if records:
        for record in records:
            display_name = task_jobs.get_display_name(record)
            click.echo(display_name)


@tasks.command(name="delete")
@click.argument("name")
@click.option(
    "--cluster",
    help="A cluster.")
@click.option(
    "--profile",
    help="An AWS profile to connect with.")
@click.option(
    "--access-key-id",
    help="An AWS access key ID.")
@click.option(
    "--access-key-secret",
    help="An AWS access key secret.")
def delete_task(
        name,
        cluster=None,
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """Delete ECS tasks."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)

    if not cluster:
        msg = "Which cluster? Use --cluster."
        raise click.ClickException(msg)
    
    try:
        task_jobs.delete(aws_profile, cluster, name)
    except PermissionDenied:
        msg = "You don't have permission to delete task definitions."
        raise click.ClickException(msg)
    except (MissingKey, Non200Response) as error:
        raise click.ClickException(str(error))
    except AwsError as error:
        raise click.ClickException(str(error))
    except (ResourceDoesNotExist, ResourceAlreadyExists, ResourceNotDeleted) as error:
        raise click.ClickException(str(error))
