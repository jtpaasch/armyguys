# -*- coding: utf-8 -*-

"""Commands for managing S3 buckets."""

import click

from ...jobs import s3buckets as s3_jobs

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
def s3buckets():
    """Manage S3 buckets."""
    pass


@s3buckets.command(name="beanstalk")
@click.option(
    "--profile",
    help="An AWS profile to connect with.")
@click.option(
    "--access-key-id",
    help="An AWS access key ID.")
@click.option(
    "--access-key-secret",
    help="An AWS access key secret.")
def list_elasticbeanstalk_s3_buckets(
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """List S3 buckets used by Elastic Beanstalk."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)

    try:
        beanstalk_bucket = s3_jobs.fetch_beanstalk_bucket(aws_profile)
    except PermissionDenied:
        msg = "You don't have premission to view Elastic Beanstalk S3 buckets."
        raise click.ClickException(msg)
    except (MissingKey, Non200Response) as error:
        raise click.ClickException(str(error))
    except AwsError as error:
        raise click.ClickException(str(error))

    if beanstalk_bucket:
        click.echo(beanstalk_bucket)


@s3buckets.command(name="list")
@click.option(
    "--profile",
    help="An AWS profile to connect with.")
@click.option(
    "--access-key-id",
    help="An AWS access key ID.")
@click.option(
    "--access-key-secret",
    help="An AWS access key secret.")
def list_s3_buckets(
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """List S3 buckets."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)

    try:
        buckets = s3_jobs.fetch_all(aws_profile)
    except PermissionDenied:
        msg = "You don't have premission to view S3 buckets."
        raise click.ClickException(msg)
    except (MissingKey, Non200Response) as error:
        raise click.ClickException(str(error))
    except AwsError as error:
        raise click.ClickException(str(error))

    if buckets:
        for bucket in buckets:
            display_name = s3_jobs.get_display_name(bucket)
            click.echo(display_name)

@s3buckets.command(name="create")
@click.argument("name")
@click.option(
    "--private",
    is_flag=True,
    help="Is it a private bucket?")
@click.option(
    "--profile",
    help="An AWS profile to connect with.")
@click.option(
    "--access-key-id",
    help="An AWS access key ID.")
@click.option(
    "--access-key-secret",
    help="An AWS access key secret.")
def create_s3_bucket(
        name,
        private=None,
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """Create s3 buckets."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)

    try:
        buckets = s3_jobs.create(aws_profile, name, private)
    except PermissionDenied:
        msg = "You don't have premission to create S3 buckets."
        raise click.ClickException(msg)
    except (MissingKey, Non200Response) as error:
        raise click.ClickException(str(error))
    except AwsError as error:
        raise click.ClickException(str(error))
    except (ResourceDoesNotExist, ResourceAlreadyExists, ResourceNotCreated) as error:
        raise click.ClickException(str(error))

    if buckets:
        for bucket in buckets:
            display_name = s3_jobs.get_display_name(bucket)
            click.echo(display_name)


@s3buckets.command(name="delete")
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
def delete_s3_bucket(
        name,
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """Delete s3 buckets."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)

    try:
        buckets = s3_jobs.delete(aws_profile, name)
    except PermissionDenied:
        msg = "You don't have premission to delete S3 buckets."
        raise click.ClickException(msg)
    except (MissingKey, Non200Response) as error:
        raise click.ClickException(str(error))
    except AwsError as error:
        raise click.ClickException(str(error))
    except (ResourceDoesNotExist, ResourceNotDeleted) as error:
        raise click.ClickException(str(error))

