# -*- coding: utf-8 -*-

"""Commands for managing launch configurations."""

import click

from ...jobs import launchconfigurations as launchconfig_jobs

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
def launchconfigs():
    """Manage launch configurations."""
    pass


@launchconfigs.command(name="list")
@click.option(
    "--profile",
    help="An AWS profile to connect with.")
@click.option(
    "--access-key-id",
    help="An AWS access key ID.")
@click.option(
    "--access-key-secret",
    help="An AWS access key secret.")
def list_launch_configs(
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """List launch configurations."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)

    try:
        records = launchconfig_jobs.fetch_all(aws_profile)
    except PermissionDenied:
        msg = "You don't have premission to view launch configurations."
        raise click.ClickException(msg)
    except (MissingKey, Non200Response) as error:
        raise click.ClickException(str(error))
    except AwsError as error:
        raise click.ClickException(str(error))

    if records:
        for record in records:
            display_name = launchconfig_jobs.get_display_name(record)
            click.echo(display_name)


@launchconfigs.command(name="create")
@click.argument("name")
@click.option(
    "--ami",
    help="An AMI ID.")
@click.option(
    "--instance-type",
    default="t2.micro",
    help="An EC2 instance type.")
@click.option(
    "--key-pair",
    help="The name of a key pair.")
@click.option(
    "--security-group",
    multiple=True,
    help="The name or ID of a security group.")
@click.option(
    "--public-ip",
    is_flag=True,
    help="Do EC2 instances get public IPs?")
@click.option(
    "--instance-profile",
    help="An instance profile for the EC2 instances.")
@click.option(
    "--user-data-file",
    multiple=True,
    help="TYPE:FILEPATH, e.g., text/x-shellscript:foo.sh")
@click.option(
    "--user-data",
    multiple=True,
    help="TYPE:CONTENTS, e.g., 'text/x-shellscript:#/bin/bash \n touch logs'")
@click.option(
    "--profile",
    help="An AWS profile to connect with.")
@click.option(
    "--access-key-id",
    help="An AWS access key ID.")
@click.option(
    "--access-key-secret",
    help="An AWS access key secret.")
def create_launch_config(
        name,
        ami=None,
        instance_type=None,
        key_pair=None,
        security_group=None,
        public_ip=None,
        instance_profile=None,
        user_data_file=None,
        user_data=None,
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """Create launch configurations."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)

    user_data_files = utils.parse_user_data_files(user_data_file)
    user_data = utils.parse_user_data(user_data)

    try:
        records = launchconfig_jobs.create(
            aws_profile,
            name,
            ami,
            instance_type,
            key_pair,
            security_groups=security_group,
            public_ip=public_ip,
            instance_profile=instance_profile,
            user_data_files=user_data_files,
            user_data=user_data)
    except PermissionDenied:
        msg = "You don't have premission to create launch configurations."
        raise click.ClickException(msg)
    except (MissingKey, Non200Response) as error:
        raise click.ClickException(str(error))
    except AwsError as error:
        raise click.ClickException(str(error))
    except (ResourceDoesNotExist, ResourceAlreadyExists, ResourceNotCreated) as error:
        raise click.ClickException(str(error))

    if records:
        for record in records:
            display_name = launchconfig_jobs.get_display_name(record)
            click.echo(display_name)


@launchconfigs.command(name="delete")
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
def delete_launch_config(
        name,
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """Delete launch configurations."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)

    try:
        launchconfig_jobs.delete(aws_profile, name)
    except PermissionDenied:
        msg = "You don't have premission to delete launch configurations."
        raise click.ClickException(msg)
    except (MissingKey, Non200Response) as error:
        raise click.ClickException(str(error))
    except AwsError as error:
        raise click.ClickException(str(error))
    except (ResourceDoesNotExist, ResourceNotDeleted) as error:
        raise click.ClickException(str(error))
