# -*- coding: utf-8 -*-

"""Commands for managing load balancers."""

import click

from ...jobs import loadbalancers as loadbalancer_jobs

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
def loadbalancers():
    """Manage load balancers."""
    pass


@loadbalancers.command(name="list")
@click.option(
    "--profile",
    help="An AWS profile to connect with.")
@click.option(
    "--access-key-id",
    help="An AWS access key ID.")
@click.option(
    "--access-key-secret",
    help="An AWS access key secret.")
def list_load_balancers(
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """List load balancers."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)

    try:
        records = loadbalancer_jobs.fetch_all(aws_profile)
    except PermissionDenied:
        msg = "You don't have premission to view load balancers."
        raise click.ClickException(msg)
    except (MissingKey, Non200Response) as error:
        raise click.ClickException(str(error))
    except AwsError as error:
        raise click.ClickException(str(error))

    if records:
        for record in records:
            display_name = loadbalancer_jobs.get_display_name(record)
            click.echo(display_name)


@loadbalancers.command(name="create")
@click.argument("name")
@click.option(
    "--listen",
    multiple=True,
    help="PROTOCOL:PORT")
@click.option(
    "--security-group",
    multiple=True,
    help="A security group.")
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
    "--tag",
    multiple=True,
    help="KEY:VALUE")
@click.option(
    "--profile",
    help="An AWS profile to connect with.")
@click.option(
    "--access-key-id",
    help="An AWS access key ID.")
@click.option(
    "--access-key-secret",
    help="An AWS access key secret.")
def create_load_balancer(
        name,
        listen=None,
        security_group=None,
        zone=None,
        subnet=None,
        vpc=None,
        tag=None,
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """Create load balancers."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)

    tags = utils.parse_tags(tag)
    listeners = utils.parse_listeners(listen)
    
    try:
        records = loadbalancer_jobs.create(
            aws_profile,
            name,
            listeners,
            security_group,
            zone,
            subnet,
            vpc)
    except PermissionDenied:
        msg = "You don't have premission to create load balancers."
        raise click.ClickException(msg)
    except (MissingKey, Non200Response) as error:
        raise click.ClickException(str(error))
    except AwsError as error:
        raise click.ClickException(str(error))
    except (ResourceDoesNotExist, ResourceAlreadyExists, ResourceNotCreated) as error:
        raise click.ClickException(str(error))

    if records:
        for record in records:
            display_name = loadbalancer_jobs.get_display_name(record)
            click.echo(display_name)


@loadbalancers.command(name="delete")
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
def delete_load_balancer(
        name,
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """Delete load balancers."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)

    try:
        loadbalancer_jobs.delete(aws_profile, name)
    except PermissionDenied:
        msg = "You don't have premission to delete load balancers."
        raise click.ClickException(msg)
    except (MissingKey, Non200Response) as error:
        raise click.ClickException(str(error))
    except AwsError as error:
        raise click.ClickException(str(error))
    except (ResourceDoesNotExist, ResourceNotDeleted) as error:
        raise click.ClickException(str(error))
    except WaitTimedOut as error:
        raise click.ClickException(str(error))
