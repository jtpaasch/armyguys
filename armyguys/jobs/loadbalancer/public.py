# -*- coding: utf-8 -*-

"""For creating a public load balancer."""

from ...aws import loadbalancer
from ...aws import profile
from ...aws import securitygroup
from ...aws import subnet

from ...jobs import utils


def create_loadbalancer(
        aws_profile,
        loadbalancer_name,
        listeners=None,
        vpc_id=None,
        availability_zones=None,
        security_groups=None):
    """Create a public facing load balancer."""
    # TODO: Make sure the load balancer, security group doesn't exist.

    # Make sure we have a VPC or availability zones.
    if not vpc_id and not availability_zones:
        utils.error("Specify 'vpc_id' or 'availability_zones'.")
        utils.exit()

    # If we're deploying into a VPC, get all available subnets.
    utils.heading("Getting subnet IDs")
    subnet_ids = None
    if not vpc_id:
        utils.echo("Not launching into a VPC. Subnets n/a.")
    else:
        response = subnet.get(profile=aws_profile)
        utils.echo_data(response)
        all_subnets = response["Subnets"]
        subnet_ids = [x["SubnetId"] for x in all_subnets if x["VpcId"] == vpc_id]
        utils.emphasize("SUBNET IDs: " + str(subnet_ids))

    # Create a security group for this load balancer.
    # But only for VPCs. Security groups don't apply
    # to load balancers outside VPCs.
    utils.heading("Creating security group")
    if not vpc_id:
        utils.echo("Not launching into a VPC. Security groups n/a.")
    else:
        params = {}
        params["profile"] = aws_profile
        params["name"] = loadbalancer_name + "--security-group"
        params["vpc"] = vpc_id
        response = securitygroup.create(**params)
        utils.echo_data(response)
        securitygroup_id = response["GroupId"]
        utils.emphasize("GROUP ID: " + str(securitygroup_id))

        # Tag the security group.
        utils.heading("Tagging security group")
        params = {}
        params["profile"] = aws_profile
        params["security_group"] = securitygroup_id
        params["key"] = "Load Balancer"
        params["value"] = loadbalancer_name
        response = securitygroup.tag(**params)
        utils.echo_data(response)
        utils.emphasize("TAG NAME: " + str(params["key"]))
        utils.emphasize("TAG VALUE: " + str(params["value"]))

        # Add the security group to the list.
        if security_groups:
            security_groups.append(securitygroup_id)
        else:
            security_groups = [securitygroup_id]
    
    # Create the load balancer.
    utils.heading("Creating load balancer")
    params = {}
    params["profile"] = aws_profile
    params["name"] = loadbalancer_name
    if listeners:
        params["listeners"] = listeners
    if subnet_ids:
        params["subnets"] = subnet_ids
    elif availability_zones:
        params["availability_zones"] = availability_zones
    if security_groups:
        params["security_groups"] = security_groups
    response = loadbalancer.create(**params)
    utils.echo_data(response)

    # Tag the load balancer.
    utils.heading("Tagging load balancer")
    params = {}
    params["profile"] = aws_profile
    params["load_balancer"] = loadbalancer_name
    params["key"] = "Purpose"
    params["value"] = "Public-facing load balancer."
    response = loadbalancer.tag(**params)
    utils.echo_data(response)
    utils.emphasize("TAG NAME: " + str(params["key"]))
    utils.emphasize("TAG VALUE: " + str(params["value"]))

    # Exit nicely.
    utils.echo("Done.")


if __name__ == "__main__":
    # Get an AWS profile.
    aws_profile = profile.configured()

    # Set some parameters.
    loadbalancer_name = "joe-loadbalancer"
    availability_zones = None  # ["us-east-1c", "us-east-1e"]
    vpc_id = "vpc-8c65bce8"  # None

    # Create the load balancer.
    create_loadbalancer(
        aws_profile=aws_profile,
        loadbalancer_name=loadbalancer_name,
        vpc_id=vpc_id,
        availability_zones=availability_zones)
