# -*- coding: utf-8 -*-

"""Commands for ECS clusters."""

import click

from ....jobs.autoscaling import launchconfiguration as launch_config_jobs
from ....jobs.ecs import clusters as cluster_jobs
from ....jobs import regions as region_jobs
from ....jobs import securitygroups as sg_jobs
from ....jobs import vpcs as vpc_jobs

from ...reporters import aws as aws_reporter
from ...reporters import clusters as cluster_reporter
from ...reporters import jobs as job_reporter
from ...reporters import vpc as vpc_reporter
from ...reporters import reporting

from ... import utils

@click.group()
def clusters():
    """Manage ECS clusters."""
    pass


@clusters.command(name="list")
@click.option(
    "--report",
    multiple=True,
    default=["quiet"],
    help="Report about records, jobs, AWS.")
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
        report=None,
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """List ECS clusters."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)
    reports = reporting.parse(report)
    job_reporter.message(reports, "Listing clusters...")

    # Fetch the clusters.
    job_reporter.job(reports, "Fetching clusters")
    clusters = cluster_jobs.fetch.get_all(
        profile=aws_profile,
        reports=reports,
        aws_reporter=aws_reporter.response)
    
    # Report the clusters.
    if clusters:
        job_reporter.data(reports, clusters)
    else:
        job_reporter.message(reports, "No clusters.")
    cluster_reporter.cluster_name(reports, clusters)

    job_reporter.message(reports, "")
    job_reporter.message(reports, "Done.")
    

@clusters.command(name="create")
@click.argument("name")
@click.option(
    "--vpc",
    help="A VPC ID.")
@click.option(
    "--security-group",
    multiple=True,
    help="A security group ID.")
@click.option(
    "--tag",
    multiple=True,
    help="KEY:VALUE.")
@click.option(
    "--instance-type",
    default="t2.micro",
    help="EC2 instance type.")
@click.option(
    "--key-pair",
    help="Key pair for EC2 instances.")
@click.option(
    "--instance-profile",
    help="An ECS-enabled instance profile.")
@click.option(
    "--report",
    multiple=True,
    default=["quiet"],
    help="Report about records, jobs, AWS.")
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
        vpc=None,
        security_group=None,
        tag=None,
        instance_type=None,
        key_pair=None,
        instance_profile=None,
        report=None,
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """Create an ECS cluster called NAME."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)    
    reports = reporting.parse(report)

    reporters = {}
    reporters["reports"] = reports
    reporters["aws_reporter"] = aws_reporter.response
    reporters["job_heading_reporter"] = job_reporter.job
    reporters["job_result_reporter"] = job_reporter.data

    reporters_just_text = reporters.copy()
    reporters_just_text["job_result_reporter"] = job_reporter.message

    job_reporter.message(reports, "Creating cluster...")

    # Make a list of security groups, and add to the list
    # any security groups provided by the user.
    security_groups = []
    if security_group:
        security_groups = security_group

    # Make a list of tags we can add to AWS resources.
    job_reporter.job(reports, "Parsing tags")
    tags = utils.parse_tags(tag)
    tags.append({"Name": "ECS cluster", "Value": name})
    job_reporter.tags(reports, tags)

    # If a VPC was specified, make sure it exists.
    if vpc:
        response = vpc_jobs.fetch.get_by_ID(aws_profile, vpc, **reporters)
        if not response:
            msg = "No such VPC: '" + str(vpc) + "'."
            raise click.ClickException(msg)

    # Get the subnets or availability zones.
    subnets = None
    zones = None
    response = region_jobs.fetch.get_all(aws_profile, vpc, **reporters)
    if response:
        subnets = response.get("subnets")
        zones = response.get("zones")

    # Make sure the cluster's security group doesn't exist already.
    cluster_sg = name + "--security-group"
    response = sg_jobs.fetch.get_by_name(aws_profile, cluster_sg, **reporters)
    if response:
        msg = "Security group '" + str(cluster_sg) + "' already exists."
        raise click.ClickException(msg)

    # Create the cluster's security group.
    cluster_sg_id = sg_jobs.construction.create(
        aws_profile,
        cluster_sg,
        vpc,
        tags,
        **reporters_just_text)
    if not cluster_sg_id:
        msg = "Failed to create security group '" + str(cluster_sg) + "'."
        raise click.ClickException(msg)

    # Add new security group to the list.
    if security_groups:
        security_groups.append(cluster_sg_id)
    else:
        security_groups = [cluster_sg_id]

    # Create the cluster.
    response = cluster_jobs.construction.create(
        aws_profile,
        name,
        **reporters)
    if not response:
        msg = "Failed to create cluster '" + str(name) + "'."
        raise click.ClickException(msg)

    # Create the launch config.
    init_script = None
    cluster_launch_configuration = name + "--launch-configuration"
    params = {}
    params["profile"] = aws_profile
    params["name"] = cluster_launch_configuration
    params["instance_type"] = instance_type
    if instance_profile:  # TO DO: Create a profile automatically.
        params["instance_profile"] = instance_profile
    params["security_groups"] = security_groups
    if key_pair:
        params["key_pair"] = key_pair
    if init_script:
        params["user_data"] = init_script
    params["public_ip"] = True if vpc else False
    params.update(reporters_just_text)
    response = launch_config_jobs.construction.create(**params)
    if not response:
        msg = "Failed to create launch configuration."
        raise click.ClickException(msg)

    # Create the auto scaling group.
    

    # Add ECS config as one of the tags.
    # Tag the auto scaling group.


    job_reporter.message(reports, "")
    job_reporter.message(reports, "Done.")
