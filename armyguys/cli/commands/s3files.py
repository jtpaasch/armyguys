# -*- coding: utf-8 -*-

"""Commands for managing S3 files."""

import click

from ...jobs import s3files as s3_jobs

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
def s3files():
    """Manage S3 files."""
    pass


@s3files.command(name="list")
@click.argument("bucket")
@click.option(
    "--profile",
    help="An AWS profile to connect with.")
@click.option(
    "--access-key-id",
    help="An AWS access key ID.")
@click.option(
    "--access-key-secret",
    help="An AWS access key secret.")
def list_s3_files(
        bucket,
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """List S3 files."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)

    try:
        files = s3_jobs.fetch_all(aws_profile, bucket)
    except PermissionDenied:
        msg = "You don't have premission to view S3 files."
        raise click.ClickException(msg)
    except (MissingKey, Non200Response) as error:
        raise click.ClickException(str(error))
    except AwsError as error:
        raise click.ClickException(str(error))
    except ResourceDoesNotExist as error:
        raise click.ClickException(str(error))

    if files:
        for record in files:
            display_name = s3_jobs.get_display_name(record)
            click.echo(display_name)

@s3files.command(name="create")
@click.argument("bucket")
@click.argument("name")
@click.argument("filepath", type=click.Path(exists=True))
@click.option(
    "--profile",
    help="An AWS profile to connect with.")
@click.option(
    "--access-key-id",
    help="An AWS access key ID.")
@click.option(
    "--access-key-secret",
    help="An AWS access key secret.")
def create_s3_file(
        bucket,
        name,
        filepath,
        private=None,
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """Create s3 files."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)

    try:
        files = s3_jobs.create(aws_profile, bucket, name, filepath)
    except PermissionDenied:
        msg = "You don't have premission to create S3 files."
        raise click.ClickException(msg)
    except (MissingKey, Non200Response) as error:
        raise click.ClickException(str(error))
    except AwsError as error:
        raise click.ClickException(str(error))
    except (ResourceDoesNotExist, ResourceAlreadyExists, ResourceNotCreated) as error:
        raise click.ClickException(str(error))

    if files:
        for record in files:
            display_name = s3_jobs.get_display_name(record)
            click.echo(display_name)


@s3files.command(name="delete")
@click.argument("bucket")
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
def delete_s3_file(
        bucket,
        name,
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """Delete s3 files."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)

    try:
        s3_jobs.delete(aws_profile, bucket, name)
    except PermissionDenied:
        msg = "You don't have premission to delete S3 files."
        raise click.ClickException(msg)
    except (MissingKey, Non200Response) as error:
        raise click.ClickException(str(error))
    except AwsError as error:
        raise click.ClickException(str(error))
    except (ResourceDoesNotExist, ResourceNotDeleted) as error:
        raise click.ClickException(str(error))
