# -*- coding: utf-8 -*-

"""Commands for managing auto scaling groups."""

import click

from ...jobs import clusters as cluster_jobs

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
def clusters():
    """Manage ECS clusters."""
    pass


@clusters.command(name="list")
@click.option(
    "--profile",
    help="An AWS profile to connect with.")
@click.option(
    "--access-key-id",
    help="An AWS access key ID.")
@click.option(
    "--access-key-secret",
    help="An AWS access key secret.")
def list_clusters(
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """List ECS clusters."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)

    try:
        records = cluster_jobs.fetch_all(aws_profile)
    except PermissionDenied:
        msg = "You don't have premission to view clusters."
        raise click.ClickException(msg)
    except (MissingKey, Non200Response) as error:
        raise click.ClickException(str(error))
    except AwsError as error:
        raise click.ClickException(str(error))

    if records:
        for record in records:
            display_name = cluster_jobs.get_display_name(record)
            click.echo(display_name)


@clusters.command(name="create")
@click.argument("name")
@click.option(
    "--instance-type",
    help="An EC2 instance type.")
@click.option(
    "--key-pair",
    help="The name of a key pair.")
@click.option(
    "--security-group",
    multiple=True,
    help="The name or ID of a security group.")
@click.option(
    "--instance-profile",
    help="An instance profile for the EC2 instances.")
@click.option(
    "--user-data-file",
    multiple=True,
    help="TYPE:FILEPATH, e.g., text/x-shellscript:foo.sh.")
@click.option(
    "--user-data",
    multiple=True,
    help="TYPE:CONTENTS, e.g., 'text/x-shellscript:#/bin/bash \n touch logs'")
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
    "--tag",
    multiple=True,
    help="KEY:VALUE tag.")
@click.option(
    "--dockerhub-email",
    help="Email for a Docker Hub account.")
@click.option(
    "--dockerhub-username",
    help="Username for a Docker Hub account.")
@click.option(
    "--dockerhub-password",
    help="Password for a Docker Hub account.")
@click.option(
    "--profile",
    help="An AWS profile to connect with.")
@click.option(
    "--access-key-id",
    help="An AWS access key ID.")
@click.option(
    "--access-key-secret",
    help="An AWS access key secret.")
def create_cluster(
        name,
        instance_type=None,
        key_pair=None,
        security_group=None,
        instance_profile=None,
        user_data_file=None,
        user_data=None,
        min_size=None,
        max_size=None,
        desired_size=None,
        zone=None,
        subnet=None,
        vpc=None,
        tag=None,
        dockerhub_email=None,
        dockerhub_username=None,
        dockerhub_password=None,
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """Create ECS clusters."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)

    user_data_files = utils.parse_user_data_files(user_data_file)
    user_data = utils.parse_user_data(user_data)

    tags = None
    if tag:
        tags = utils.parse_tags(tag)

    if not instance_profile:
        msg = "Which instance profile? Use --instance-profile."
        raise click.ClickException(msg)
        
    try:
        records = cluster_jobs.create(
            aws_profile,
            name,
            instance_type,
            key_pair,
            security_group,
            instance_profile,
            user_data_files,
            user_data,
            min_size,
            max_size,
            desired_size,
            zone,
            subnet,
            vpc,
            tags,
            dockerhub_email,
            dockerhub_username,
            dockerhub_password)
    except PermissionDenied:
        msg = "You don't have premission to create clusters."
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
            display_name = cluster_jobs.get_display_name(record)
            click.echo(display_name)


@clusters.command(name="delete")
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
def delete_cluster(
        name,
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """Delete ECS clusters."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)

    try:
        cluster_jobs.delete(aws_profile, name)
    except PermissionDenied:
        msg = "You don't have premission to delete clusters."
        raise click.ClickException(msg)
    except (MissingKey, Non200Response) as error:
        raise click.ClickException(str(error))
    except AwsError as error:
        raise click.ClickException(str(error))
    except (ResourceDoesNotExist, ResourceNotDeleted) as error:
        raise click.ClickException(str(error))
    except WaitTimedOut as error:
        raise click.ClickException(str(error))


@clusters.command(name="serve")
@click.argument("name")
@click.argument("loadbalancer")
@click.option(
    "--profile",
    help="An AWS profile to connect with.")
@click.option(
    "--access-key-id",
    help="An AWS access key ID.")
@click.option(
    "--access-key-secret",
    help="An AWS access key secret.")
def serve(
        name,
        loadbalancer,
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """Attach clusters to load balancers."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)

    try:
        cluster_jobs.attach_load_balancer(aws_profile, name, loadbalancer)
    except PermissionDenied:
        msg = "You don't have premission to attach load balancers."
        raise click.ClickException(msg)
    except (MissingKey, Non200Response) as error:
        raise click.ClickException(str(error))
    except ResourceDoesNotExist as error:
        raise click.ClickException(str(error))
    except AwsError as error:
        raise click.ClickException(str(error))


@clusters.command(name="unserve")
@click.argument("name")
@click.argument("loadbalancer")
@click.option(
    "--profile",
    help="An AWS profile to connect with.")
@click.option(
    "--access-key-id",
    help="An AWS access key ID.")
@click.option(
    "--access-key-secret",
    help="An AWS access key secret.")
def unserve(
        name,
        loadbalancer,
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """Detach clusters from load balancers."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)

    try:
        clusters_jobs.detach_load_balancer(aws_profile, name, loadbalancer)
    except PermissionDenied:
        msg = "You don't have premission to detach load balancers."
        raise click.ClickException(msg)
    except (MissingKey, Non200Response) as error:
        raise click.ClickException(str(error))
    except ResourceDoesNotExist as error:
        raise click.ClickException(str(error))
    except AwsError as error:
        raise click.ClickException(str(error))
