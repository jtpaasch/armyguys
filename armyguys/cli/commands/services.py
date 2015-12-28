# -*- coding: utf-8 -*-

"""Commands for managing ECS services."""

import click

from ...jobs import services as service_jobs

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
def services():
    """Manage ECS services."""
    pass


@services.command(name="list")
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
def list_services(
        cluster,
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """List ECS services."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)

    try:
        records = service_jobs.fetch_all(aws_profile, cluster)
    except PermissionDenied:
        msg = "You don't have permission to view services."
        raise click.ClickException(msg)
    except (MissingKey, Non200Response) as error:
        raise click.ClickException(str(error))
    except AwsError as error:
        raise click.ClickException(str(error))
    except ResourceDoesNotExist as error:
        raise click.ClickException(str(error))

    if records:
        for record in records:
            display_name = service_jobs.get_display_name(record)
            click.echo(display_name)


@services.command(name="create")
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
def create_service(
        name,
        cluster=None,
        task_definition=None,
        count=None,
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """Create ECS services."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)

    if not cluster:
        msg = "Which cluster? Use --cluster."
        raise click.ClickException(msg)
    if not task_definition:
        msg = "Which task definition? Use --task-definition."
        raise click.ClickException(msg)

    try:
        record = service_jobs.create(
            aws_profile,
            name,
            cluster,
            task_definition,
            count)
    except PermissionDenied:
        msg = "You don't have permission to create services."
        raise click.ClickException(msg)
    except (MissingKey, Non200Response) as error:
        raise click.ClickException(str(error))
    except AwsError as error:
        raise click.ClickException(str(error))
    except (ResourceDoesNotExist, ResourceAlreadyExists, ResourceNotCreated) as error:
        raise click.ClickException(str(error))

    if record:
        display_name = service_jobs.get_display_name(record)
        click.echo(display_name)


@services.command(name="update")
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
def update_service(
        name,
        cluster=None,
        task_definition=None,
        count=None,
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """Update ECS services."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)

    if not cluster:
        msg = "Which cluster? Use --cluster."
        raise click.ClickException(msg)

    try:
        record = service_jobs.update(
            aws_profile,
            name,
            cluster,
            task_definition,
            count)
    except PermissionDenied:
        msg = "You don't have permission to update services."
        raise click.ClickException(msg)
    except (MissingKey, Non200Response) as error:
        raise click.ClickException(str(error))
    except AwsError as error:
        raise click.ClickException(str(error))
    except (ResourceDoesNotExist, ResourceAlreadyExists, ResourceNotCreated) as error:
        raise click.ClickException(str(error))

    if record:
        display_name = service_jobs.get_display_name(record)
        click.echo(display_name)


@services.command(name="delete")
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
def delete_service(
        name,
        cluster=None,
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """Delete ECS services."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)

    if not cluster:
        msg = "Which cluster? Use --cluster."
        raise click.ClickException(msg)

    try:
        service_jobs.delete(aws_profile, cluster, name)
    except PermissionDenied:
        msg = "You don't have permission to delete services."
        raise click.ClickException(msg)
    except (MissingKey, Non200Response) as error:
        raise click.ClickException(str(error))
    except AwsError as error:
        raise click.ClickException(str(error))
    except (ResourceDoesNotExist, ResourceAlreadyExists, ResourceNotDeleted) as error:
        raise click.ClickException(str(error))
