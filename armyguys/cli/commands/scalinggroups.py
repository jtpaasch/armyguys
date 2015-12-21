# -*- coding: utf-8 -*-

"""Commands for managing auto scaling groups."""

import click

from ...jobs import autoscalinggroups as scalinggroup_jobs

from ...jobs.exceptions import AwsError
from ...jobs.exceptions import ImproperlyConfigured
from ...jobs.exceptions import MissingKey
from ...jobs.exceptions import Non200Response
from ...jobs.exceptions import PermissionDenied
from ...jobs.exceptions import ResourceAlreadyExists
from ...jobs.exceptions import ResourceDoesNotExist
from ...jobs.exceptions import ResourceNotCreated
from ...jobs.exceptions import ResourceNotDeleted
from ...jobs.exceptions import WaitTimedOut

from .. import utils


@click.group()
def scalinggroups():
    """Manage auto scaling groups."""
    pass


@scalinggroups.command(name="list")
@click.option(
    "--profile",
    help="An AWS profile to connect with.")
@click.option(
    "--access-key-id",
    help="An AWS access key ID.")
@click.option(
    "--access-key-secret",
    help="An AWS access key secret.")
def list_auto_scaling_groups(
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """List auto scaling groups."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)

    try:
        records = scalinggroup_jobs.fetch_all(aws_profile)
    except PermissionDenied:
        msg = "You don't have premission to view auto scaling groups."
        raise click.ClickException(msg)
    except (MissingKey, Non200Response) as error:
        raise click.ClickException(str(error))
    except AwsError as error:
        raise click.ClickException(str(error))

    if records:
        for record in records:
            display_name = scalinggroup_jobs.get_display_name(record)
            click.echo(display_name)


@scalinggroups.command(name="create")
@click.argument("name")
@click.option(
    "--launch-config",
    help="A launch configuration.")
@click.option(
    "--min-size",
    default=1,
    help="The min number of machines in the group.")
@click.option(
    "--max-size",
    default=1,
    help="The max number of machines in the group.")
@click.option(
    "--desired-size",
    default=1,
    help="The ideal number of machines in the group.")
@click.option(
    "--zone",
    multiple=True,
    help="An availability zone.")
@click.option(
    "--subnet",
    multiple=True,
    help="A subnet.")
@click.option(
    "--vpc",
    help="A VPC.")
@click.option(
    "--profile",
    help="An AWS profile to connect with.")
@click.option(
    "--access-key-id",
    help="An AWS access key ID.")
@click.option(
    "--access-key-secret",
    help="An AWS access key secret.")
def create_auto_scaling_group(
        name,
        launch_config,
        min_size,
        max_size,
        desired_size,
        zone=None,
        subnet=None,
        vpc=None,
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """Create auto scaling groups."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)

    if not launch_config:
        raise click.ClickException("Which launch config? Use --launch-config.")
    
    try:
        records = scalinggroup_jobs.create(
            aws_profile,
            name,
            launch_config,
            min_size,
            max_size,
            desired_size,
            zone,
            subnet,
            vpc)
    except PermissionDenied:
        msg = "You don't have premission to create auto scaling groups."
        raise click.ClickException(msg)
    except (MissingKey, Non200Response) as error:
        raise click.ClickException(str(error))
    except AwsError as error:
        raise click.ClickException(str(error))
    except (ResourceDoesNotExist, ResourceAlreadyExists, ResourceNotCreated) as error:
        raise click.ClickException(str(error))
    except ImproperlyConfigured as error:
        raise click.ClickException(str(error))

    if records:
        for record in records:
            display_name = scalinggroup_jobs.get_display_name(record)
            click.echo(display_name)


@scalinggroups.command(name="delete")
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
def delete_auto_scaling_group(
        name,
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """Delete auto scaling groups."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)

    try:
        scalinggroup_jobs.delete(aws_profile, name)
    except PermissionDenied:
        msg = "You don't have premission to delete auto scaling groups."
        raise click.ClickException(msg)
    except (MissingKey, Non200Response) as error:
        raise click.ClickException(str(error))
    except AwsError as error:
        raise click.ClickException(str(error))
    except (ResourceDoesNotExist, ResourceNotDeleted) as error:
        raise click.ClickException(str(error))
    except WaitTimedOut as error:
        raise click.ClickException(str(error))
