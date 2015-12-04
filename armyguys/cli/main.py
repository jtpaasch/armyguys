# -*- coding: utf-8 -*-

"""The ``main`` module for the ``cli`` package."""

import click

from ..aws import profile

from ..jobs import availabilityzone as zone_jobs
from ..jobs import loadbalancer as elb_jobs
from ..jobs import securitygroup as sg_jobs
from ..jobs import subnet as subnet_jobs
from ..jobs import vpc as vpc_jobs

ZONE_BLACKLIST = ["us-east-1a"]


def get_profile():
    aws_profile = profile.configured("jt-nara")
    return aws_profile


def log(message, verbose):
    if verbose:
        click.echo(message)


def log_heading(message, verbose):
    if verbose:
        click.echo("")
        click.secho(message, bold=True)


def log_emphasis(message, verbose):
    if verbose:
        click.secho(message, fg="blue")


def log_warning(message, verbose):
    if verbose:
        click.secho(message, fg="yellow")


def log_error(message, verbose):
    if verbose:
        click.secho(message, fg="red")


@click.group()
def cli():
    """Manage AWS resources."""
    pass


@cli.group()
def vpc():
    """Manage VPCs."""
    pass

@vpc.command(name="list")
def list_vpcs():
    """List VPCs."""
    aws_profile = get_profile()
    vpcs = vpc_jobs.fetch.get_all(aws_profile)
    for record in vpcs:
        if record["IsDefault"]:
            click.echo(record["VpcId"] + "*")
        else:
            click.echo(record["VpcId"])


@cli.group()
def securitygroup():
    """Manage security groups."""
    pass


@securitygroup.command(name="list")
@click.option(
    "--vpc-id",
    help="A VPC to list security groups in.")
def list_security_groups(vpc_id=None):
    """List security groups."""
    aws_profile = get_profile()
    if vpc_id:
        sgs = sg_jobs.fetch.get_all_in_vpc(aws_profile, vpc_id)
    else:
        sgs = sg_jobs.fetch.get_all(aws_profile)
    for sg in sgs:
        click.echo(sg["GroupId"])


@cli.group()
def subnet():
    """Manage subnets."""
    pass


@subnet.command(name="list")
@click.option(
    "--vpc-id",
    help="A VPC to list subnets in.")
def list_subnets(vpc_id=None):
    """List subnets."""
    aws_profile = get_profile()
    if vpc_id:
        subnets = subnet_jobs.fetch.get_all_in_vpc(aws_profile, vpc_id)
    else:
        subnets = subnet_jobs.fetch.get_all(aws_profile)
    for subnet in subnets:
        click.echo(subnet["SubnetId"])


@cli.group()
def zone():
    """Manage availibility zones."""
    pass


@zone.command(name="list")
def list_availability_zones():
    """List available availability zones."""
    aws_profile = get_profile()
    zones = zone_jobs.fetch.get_all(aws_profile)
    for zone in zones:
        click.echo(zone["ZoneName"])


@cli.group()
def loadbalancer():
    """Manage load balancers."""
    pass


@loadbalancer.command(name="list")
@click.option(
    "--vpc-id",
    help="A VPC to list subnets in.")
def list_load_balancers(vpc_id=None):
    """List load balancers."""
    aws_profile = get_profile()
    if vpc_id:
        elbs = elb_jobs.fetch.get_all_in_vpc(aws_profile, vpc_id)
    else:
        elbs = elb_jobs.fetch.get_all(aws_profile)
    for elb in elbs:
       click.echo(elb["LoadBalancerId"])


@loadbalancer.command(name="create")
@click.argument("name")
@click.option(
    "--vpc-id",
    help="A VPC to put the load balancer in.")
@click.option(
    "--verbose",
    type=int,
    default=0,
    help="Display details.")
def create_load_balancer(name, vpc_id=None, verbose=None):
    """Create a VPC called NAME."""
    aws_profile = get_profile()
    log("Creating load balancer '" + str(name) + "'.", verbose)

    # Make sure the VPC exists (if one was specified).
    log_heading("Checking if VPC exists", verbose)
    if vpc_id:
        if vpc_jobs.fetch.get_by_ID(aws_profile, vpc_id):
            log("Ok. VPC '" + str(vpc_id) + "' found.", verbose)
        else:
            msg = "No such VPC '" + str(vpc_id) + "'."
            log_error(msg, verbose)
            raise click.ClickException(msg)
    else:
        log("VPC not specified.", verbose)
    
    # If no VPC was specified, see if there's a default VPC.
    log_heading("Checking for default VPC ID", verbose)
    if not vpc_id:
        default_vpc = vpc_jobs.fetch.get_default_vpc(aws_profile)
        if default_vpc:
            vpc_id = default_vpc["VpcId"]
            log("Default VPC: " + str(vpc_id), verbose)
        else:
            log("No default VPC.", verbose)
    else:
        log("VPC provided. Default VPC n/a.", verbose)

    # If we have a VPC, let's get its subnets.
    log_heading("Getting subnets", verbose)
    subnet_ids = None
    if vpc_id:
        subnets = subnet_jobs.fetch.get_all_in_vpc(aws_profile, vpc_id)
        subnet_ids = [x["SubnetId"] for x in subnets]
        log("Subnet IDs: " + str(subnet_ids), verbose)
    else:
        log("No VPC. Subnets n/a.", verbose)

    # If we have no VPC, we need to know the availability zones.
    log_heading("Getting availability zones", verbose)
    zones = None
    if not vpc_id:
        zones = zone_jobs.fetch.get_all(aws_profile)
        zones = [x["ZoneName"] for x in zones
                 if x["ZoneName"] not in ZONE_BLACKLIST]
        log("Zones: " + str(zones), verbose) 
    else:
        log("Using VPC. Zones n/a.", verbose)

    # Does the security group exist already?
    log_heading("Checking security group", verbose)
    elb_sg = name + "--security-group"
    if sg_jobs.fetch.get_by_name(aws_profile, elb_sg):
        msg = "Security group '" + str(elb_sg) + "' already exists."
        log_error(msg, verbose)
        raise click.ClickException(msg)
    else:
        log("Ok. No security group '" + str(elb_sg) + "'.", verbose)

    # Does the load balancer exist already?
    log_heading("Checking load balancer", verbose)
    if elb_jobs.fetch.get_by_name(aws_profile, name):
        msg = "Load balancer '" + str(name) + "' already exists."
        log_error(msg, verbose)
        raise click.ClickException(msg)
    else:
        log("Ok. No load balancer '" + str(name) + "'.", verbose)

    # Create a security group for the load balancer
    # (but only for VPCs, not for EC2 Classic.)
    log_heading("Creating security group for load balancer", verbose)
    if not vpc_id:
        log("No VPC. Security group n/a.", verbose)
    else:
        params = {}
        params["profile"] = aws_profile
        params["name"] = elb_sg
        params["vpc"] = vpc_id
        response = sg_jobs.create.create(**params)
        sg_id = response["GroupId"]
        log_emphasis("GROUP ID: " + str(sg_id), verbose)


