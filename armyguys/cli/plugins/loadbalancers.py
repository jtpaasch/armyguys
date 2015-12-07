# -*- coding: utf-8 -*-

"""The ``main`` module for the ``cli`` package."""

import click

from ...jobs import loadbalancer as elb_jobs
from ...jobs import securitygroup as sg_jobs
from ...jobs import subnet as subnet_jobs
from ...jobs import vpc as vpc_jobs
from ...jobs import availabilityzone as zone_jobs

from .. import utils


@click.group()
def loadbalancers():
    """Manage load balancers."""
    pass


@loadbalancers.command(name="list")
@click.option(
    "--vpc-id",
    help="A VPC to list subnets in.")
@click.option(
    "--verbose",
    type=int,
    default=0,
    multiple=True,
    help="Display details.")
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
        vpc_id=None,
        verbose=None,
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """List load balancers."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)
    if vpc_id:
        utils.log_heading(verbose, "Fetching load balancers for " + vpc_id)
        elbs = elb_jobs.fetch.get_all_in_vpc(aws_profile, vpc_id)
    else:
        utils.log_heading(verbose, "Fetching load balancers")
        elbs = elb_jobs.fetch.get_all(aws_profile)
    if elbs:
        for elb in elbs:
            utils.echo(verbose, elb, "LoadBalancerId")
    else:
        utils.log(verbose, "No load balancers.")    


@loadbalancers.command(name="create")
@click.argument("name")
@click.option(
    "--listen",
    multiple=True,
    default=["HTTP:80"],
    help="PROTOCOL:PORT, default HTTP:80.")
@click.option(
    "--vpc-id",
    help="A VPC to put the load balancer in.")
@click.option(
    "--security-group",
    multiple=True,
    help="A security group ID (VPC only).")
@click.option(
    "--tag",
    multiple=True,
    help="KEY:VALUE.")
@click.option(
    "--verbose",
    type=int,
    default=0,
    multiple=True,
    help="Display details.")
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
        vpc_id=None,
        security_group=None,
        tag=None,
        verbose=None,
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """Create a load balancer called NAME."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)

    # We'll make a list of security groups below.
    security_groups = []
    if security_group:
        security_groups = security_group

    # Make a list of listeners.
    # TO DO: if you allow "https", you need to check for SSLCertificateId too.
    utils.log_heading(verbose, "Parsing listeners")
    listeners = []
    valid_protocols = ["http", "tcp"]
    if listen:
        for record in listen:
            listen_parts = record.split(":")
            if len(listen_parts) != 2:
                msg = "Bad listener: '" + str(record) + "'. " \
                      + "Must be PROTOCOL:PORT."
                utils.log_error(verbose, msg)
                raise click.ClickException(msg)
            protocol = listen_parts[0].lower()
            port = listen_parts[1].lower()
            if protocol not in valid_protocols:
                msg = "Bad protocol: '" + str(protocol) + "'. " \
                      + "Must be one of: " + str(valid_protocols)
                utils.log_error(verbose, msg)
                raise click.ClickException(msg)
            try:
                port = int(port)
            except ValueError:
                msg = "Bad port: '" + str(port) + "'. " \
                      + "Must be an integer."
                utils.log_error(verbose, msg)
                raise click.ClickException(msg)
            listeners.append({
                "Protocol": protocol,
                "LoadBalancerPort": port,
                "InstanceProtocol": protocol,
                "InstancePort": port
                })
    if listeners:
        for listener in listeners:
            msg = str(listener["Protocol"]) \
                  + ":" \
                  + str(listener["LoadBalancerPort"])
            utils.log(verbose, msg)
        utils.log_data(verbose, listeners)
    else:
        msg = "Unable to construct listeners."
        utils.log_error(msg)
        raise click.clickException(msg)

    # Make a list of tags.
    utils.log(verbose, "")
    utils.log_heading(verbose, "Parsing tags")
    tags = []
    if tag:
        for record in tag:
            tag_parts = record.split(":")
            if len(tag_parts) != 2:
                msg = "Bad tag: '" + str(record) + "'. " \
                      + "Must be KEY:VALUE."
                utils.log_error(verbose, msg)
                raise click.ClickException(msg)
            key = tag_parts[0]
            value = tag_parts[1]
            if all([key, value]):
                tags.append({"Name": key, "Value": value})
            elif not key:
                msg = "Empty tag key: " + str(record)
                utils.log_error(verbose, msg)
                raise click.ClickException(msg)
            elif not value:
                msg = "Empty tag value: " + str(record)
                utils.log_error(verbose, msg)
                raise click.ClickException(msg)
    if tags:
        for tag in tags:
            msg = str(tag["Name"]) + ": " + str(tag["Value"])
            utils.log(verbose, msg)
        utils.log_data(verbose, tags)
    else:
        utils.log(verbose, "No tags.")
    
    # Make sure the VPC exists (if one was specified).
    utils.log(verbose, "")
    utils.log_heading(verbose, "Checking if VPC exists")
    if vpc_id:
        vpc_data = vpc_jobs.fetch.get_by_ID(aws_profile, vpc_id)
        utils.log_data(verbose, vpc_data, "VpcId")
        if vpc_data:
            utils.log(verbose, "Ok. VPC '" + str(vpc_id) + "' found.")
        else:
            msg = "No such VPC '" + str(vpc_id) + "'."
            utils.log_error(verbose, msg)
            raise click.ClickException(msg)
    else:
        utils.log(verbose, "VPC not specified.")

    # If no VPC was specified, see if there's a default VPC.
    utils.log(verbose, "")
    utils.log_heading(verbose, "Checking for default VPC ID")
    if not vpc_id:
        default_vpc = vpc_jobs.fetch.get_default_vpc(aws_profile)
        utils.log_data(verbose, default_vpc, key="VpcId")
        if default_vpc:
            vpc_id = default_vpc["VpcId"]
            utils.log(verbose, "Default VPC: " + str(vpc_id))
        else:
            utils.log(verbose, "No default VPC.")
    else:
        utils.log(verbose, "VPC provided. Default VPC n/a.")

    # If we have a VPC, let's get its subnets.
    utils.log(verbose, "")
    utils.log_heading(verbose, "Getting subnets")
    subnet_ids = None
    if vpc_id:
        subnets = subnet_jobs.fetch.get_all_in_vpc(aws_profile, vpc_id)
        utils.log_data(verbose, subnets)
        subnet_ids = [x["SubnetId"] for x in subnets]
        utils.log(verbose, "Subnet IDs: " + str(subnet_ids))
    else:
        utils.log(verbose, "No VPC. Subnets n/a.")

    # If we have no VPC, we need to know the availability zones.
    utils.log(verbose, "")
    utils.log_heading(verbose, "Getting availability zones")
    zones = None
    if not vpc_id:
        zones = zone_jobs.fetch.get_all(aws_profile)
        utils.log_data(verbose, zones)
        utils.log(verbose, "Zones: " + str(zones))
    else:
        utils.log(verbose, "Using VPC. Zones n/a.")

    # Does the security group exist already?
    utils.log(verbose, "")
    utils.log_heading(verbose, "Checking security group")
    elb_sg = name + "--security-group"
    sg_data = sg_jobs.fetch.get_by_name(aws_profile, elb_sg)
    utils.log_data(verbose, sg_data)
    if sg_data:
        msg = "Security group '" + str(elb_sg) + "' already exists."
        utils.log_error(verbose, msg)
        raise click.ClickException(msg)
    else:
        utils.log(verbose, "Ok. No security group '" + str(elb_sg) + "'.")

    # Does the load balancer exist already?
    utils.log(verbose, "")
    utils.log_heading(verbose, "Checking load balancer")
    elb_data = elb_jobs.fetch.get_by_name(aws_profile, name)
    utils.log_data(verbose, elb_data)
    if elb_data:
        msg = "Load balancer '" + str(name) + "' already exists."
        utils.log_error(verbose, msg)
        raise click.ClickException(msg)
    else:
        utils.log(verbose, "Ok. No load balancer '" + str(name) + "'.")

    # Create a security group for the load balancer,
    # but only for VPCs, not for EC2 Classic.
    utils.log(verbose, "")
    utils.log_heading(verbose, "Creating security group for load balancer")
    security_group_id = None
    if not vpc_id:
        utils.log(verbose, "No VPC. Security group n/a.")
    else:
        params = {}
        params["profile"] = aws_profile
        params["name"] = elb_sg
        params["vpc"] = vpc_id
        response = sg_jobs.build.create(**params)
        security_group_id = response["GroupId"]
        utils.log_data(verbose, response, "GroupId")
        utils.log(verbose, "Group ID: " + str(security_group_id))

    # Tag the security group with the load balancer's name.
    utils.log(verbose, "")
    utils.log_heading(verbose, "Tagging load balancer's security group")
    if not vpc_id:
        utils.log(verbose, "No VPC. Security group n/a.")
    else:
        params = {}
        params["profile"] = aws_profile
        params["security_group"] = security_group_id
        params["key"] = "Load Balancer"
        params["value"] = name
        response = sg_jobs.build.tag(**params)
        utils.log_data(verbose, response)
        msg = str(params["key"]) + ": " + str(params["value"])
        utils.log(verbose, msg)

        # Add any tags provided by the user.
        if tags:
            for tag in tags:
                params = {}
                params["profile"] = aws_profile
                params["security_group"] = security_group_id
                params["key"] = tag["Name"]
                params["value"] = tag["Value"]
                response = sg_jobs.build.tag(**params)
                utils.log_data(verbose, response)
                msg = str(params["key"]) + ": " + str(params["value"])
                utils.log(verbose, msg)

    # Add the new security group to the list of
    # user provided groups (if any were provided).
    utils.log(verbose, "")
    utils.log_heading(verbose, "Appending security group to the list")
    if not vpc_id:
        utils.log(verbose, "No VPC. Adding security group n/a.")
    else:
        if security_groups:
            security_groups.append(security_group_id)
        else:
            security_groups = [security_group_id]
    utils.log(verbose, "Security groups: " + str(security_groups))

    # Create the load balancer.
    utils.log(verbose, "")
    utils.log_heading(verbose, "Creating load balancer")
    params = {}
    params["profile"] = aws_profile
    params["name"] = name
    params["listeners"] = listeners
    if security_groups:
        params["security_groups"] = security_groups
    if subnet_ids:
        params["subnets"] = subnet_ids
    elif zones:
        params["availability_zones"] = zones
    response = elb_jobs.build.create(**params)
    elb_dnsname = response.get("DNSName")
    if elb_dnsname:
        utils.echo(verbose, response, key="DNSName")
    else:
        msg = "Load balancer not created."
        utils.log_error(msg)
        raise click.ClickException(msg)

    # Tag the load balancer.
    utils.log(verbose, "")
    utils.log_heading(verbose, "Tagging load balancer")
    if not tags:
        utils.log(verbose, "No tags provided. Tagging n/a.")
    else:
        for tag in tags:
            params = {}
            params["profile"] = aws_profile
            params["load_balancer"] = name
            params["key"] = tag["Name"]
            params["value"] = tag["Value"]
            response = elb_jobs.build.tag(**params)
            utils.log_data(verbose, response)
            msg = str(params["key"]) + ": " + str(params["value"])
            utils.log(verbose, msg)
    
    # Note that we're done.
    utils.log(verbose, "")
    utils.log(verbose, "Done.")


@loadbalancers.command(name="delete")
@click.argument("name")
@click.option(
    "--verbose",
    type=int,
    default=0,
    multiple=True,
    help="Display details.")
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
        verbose=None,
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """Delete a load balancer called NAME."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)
    has_security_group = False
    security_group_id = None
    has_load_balancer = False

    # Does the security group exist already?
    utils.log_heading(verbose, "Checking security group")
    elb_sg = name + "--security-group"
    sg_data = sg_jobs.fetch.get_by_name(aws_profile, elb_sg)
    utils.log_data(verbose, sg_data)
    if sg_data:
        has_security_group = True
        security_group_id = sg_data["GroupId"]
        msg = "Security group '" + str(elb_sg) + "' found."
        utils.log(verbose, msg)
    else:
        msg = "No security group '" + str(elb_sg) + "'."
        utils.log(verbose, msg)

    # Does the load balancer exist already?
    utils.log(verbose, "")
    utils.log_heading(verbose, "Checking load balancer")
    elb_data = elb_jobs.fetch.get_by_name(aws_profile, name)
    utils.log_data(verbose, elb_data)
    if elb_data:
        has_load_balancer = True
        msg = "Load balancer '" + str(name) + "' found."
        utils.log(verbose, msg)
    else:
        msg = "No load balancer '" + str(name) + "'."
        utils.log(verbose, msg)

    # Delete the load balancer.
    utils.log(verbose, "")
    utils.log_heading(verbose, "Deleting load balancer")
    if not has_load_balancer:
        msg = "No load balancer found. Deleting n/a."
        utils.log(verbose, msg)
    else:
        elb_data = elb_jobs.destroy.delete(aws_profile, name)
        utils.log_data(verbose, elb_data)
        if elb_data:
            utils.log(verbose, "Load balancer deleted.")
        else:
            msg = "No response received."
            utils.log_error(verbose, msg)

    # Delete the security group.
    utils.log(verbose, "")
    utils.log_heading(verbose, "Deleting security group")
    if not has_security_group:
        msg = "No security found. Deleting n/a."
        utils.log(verbose, msg)
    else:
        success = sg_jobs.destroy.try_to_delete(aws_profile, security_group_id)
        if success:
            utils.log(verbose, "Security group gone.")
        else:
            utils.log(verbose, "Security group not deleted. Attempt timed out.")

    # Note that we're done.
    utils.log(verbose, "")
    utils.log(verbose, "Done.")
