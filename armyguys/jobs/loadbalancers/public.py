# -*- coding: utf-8 -*-

"""For creating a public load balancer."""

from time import sleep

from ...aws import loadbalancer
from ...aws import profile
from ...aws import securitygroup
from ...aws import subnet

from ...jobs import utils


def get_security_group_name(load_balancer):
    """Get the name for a load balancer's security group.

    Args:

        load_balancer
            The name of the load balancer.

    Returns:
        The security group name (a string).

    """
    return load_balancer + "--security-group"


def get_security_group_info(aws_profile, security_group):
    """Get info about a security group.

    Args:

        aws_profile
            A profile to connect to AWS with.

        security_group
            The name of the security group to fetch info about.

    Returns:
        The JSON response returned by boto3.

    """
    response = securitygroup.get(aws_profile, security_group)
    security_groups = response["SecurityGroups"]
    result = []
    if security_groups:
        result = [x for x in security_groups
                  if x["GroupName"] == security_group]
    return result


def get_load_balancer_info(aws_profile, load_balancer):
    """Get info about a load balancer.

    Args:

        aws_profile
            A profile to connect to AWS with.

        load_balancer
            The name of the load balancer to fetch info about.

    Returns:
        The JSON response returned by boto3.

    """
    result = []
    response = loadbalancer.get(aws_profile, load_balancer)
    if response:
        load_balancers = response["LoadBalancerDescriptions"]
        if load_balancers:
            result = [x for x in load_balancers
                      if x["LoadBalancerName"] == load_balancer]
    return result


def create_load_balancer(
        aws_profile,
        name,
        listeners=None,
        vpc_id=None,
        availability_zones=None,
        security_groups=None):
    """Create a public facing load balancer.

    Args:

        aws_profile
            A profile to connect to AWS with.

        name
            The name you want to give to the load balancer.

        listeners
             A dictionary of listeners. See boto3's documentation.
             If this is omitted, the load balancer will
             listen on port 80 for HTTP traffic.

        vpc_id
            The ID of a VPC to launch the load balancer into.
            If you don't want to launch into a VPC, leave this
            field blank and fill in the ``availability_zones``
            parameter.

        availability_zones
            A list of availability zones to launch the load
            balancer into. If you want to launch into a VPC,
            leave this field blank and fill in the ``vpc_id``
            parameter.

        security_groups
            A list of security group IDs for the load balancer.

    """
    # Make sure we have a VPC or availability zones.
    if not vpc_id and not availability_zones:
        utils.error("Specify 'vpc_id' or 'availability_zones'.")
        utils.exit()

    # Make sure the security group doesn't exist.
    elb_security_group = get_security_group_name(name)
    utils.heading("Checking that the ELB's security group doesn't exist")
    response = get_security_group_info(aws_profile, elb_security_group)
    utils.echo_data(response)
    if response:
        msg = "Security group '" + elb_security_group + "' already exists."
        utils.error(msg)
        utils.exit()
    else:
        msg = "OK. No security group '" + elb_security_group + "'."
        utils.emphasize(msg)

    # Make sure the load balancer doesn't exist.
    utils.heading("Checking that the load balancer doesn't exist")
    response = get_load_balancer_info(
        aws_profile,
        name)
    utils.echo_data(response)
    if response:
        msg = "Load balancer '" + name + "' already exists."
        utils.error(msg)
        utils.exit()
    else:
        msg = "OK. No load balancer '" + name + "'."
        utils.emphasize(msg)

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
        params["name"] = elb_security_group
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
        params["value"] = name
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
    params["name"] = name
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
    params["load_balancer"] = name
    params["key"] = "Purpose"
    params["value"] = "Public-facing load balancer."
    response = loadbalancer.tag(**params)
    utils.echo_data(response)
    utils.emphasize("TAG NAME: " + str(params["key"]))
    utils.emphasize("TAG VALUE: " + str(params["value"]))

    # Exit nicely.
    utils.echo("")
    utils.echo("Done.")


def delete_load_balancer(
        aws_profile,
        load_balancer):
    """Delete a load balancer.

    Args:

        aws_profile
            A profile to connect to AWS with.

        load_balancer
            The name you want to give to the load balancer.

    """
    has_security_group = False
    has_load_balancer = False

    # Make sure the security group exists.
    elb_security_group = get_security_group_name(load_balancer)
    elb_security_group_id = None
    utils.heading("Checking that the ELB's security group exists")
    response = get_security_group_info(aws_profile, elb_security_group)
    utils.echo_data(response)
    if response:
        has_security_group = True
        elb_security_group_id = response[0]["GroupId"]
        msg = "OK. Security group '" + elb_security_group + "' found."
        utils.emphasize(msg)
    else:
        msg = "No such security group '" + elb_security_group + "'."
        utils.error(msg)

    # Make sure the load balancer exists.
    utils.heading("Checking that the load balancer exists")
    response = get_load_balancer_info(
        aws_profile,
        load_balancer)
    utils.echo_data(response)
    if response:
        has_load_balancer = True
        msg = "OK. Load balancer '" + load_balancer + "' found."
        utils.emphasize(msg)
    else:
        msg = "No such load balancer '" + load_balancer + "'."
        utils.error(msg)

    # Delete the load balancer.
    utils.heading("Deleting load balancer")
    if not has_load_balancer:
        utils.echo("No load balancer found. Deleting n/a.")
    else:
        params = {}
        params["profile"] = aws_profile
        params["load_balancer"] = load_balancer
        response = loadbalancer.delete(**params)
        utils.echo_data(response)

    # Delete the security group.
    utils.heading("Deleting security group")
    if not has_security_group:
        utils.echo("No security group found. Deleting n/a.")
    else:
        params = {}
        params["profile"] = aws_profile
        params["security_group"] = elb_security_group_id
        params["max_attempts"] = 10
        params["wait_interval"] = 1
        success = securitygroup.try_to_delete(**params)
        if success:
            utils.echo("Security group gone.")
        else:
            utils.error("Security group not deleted.")

    # Exit nicely.
    utils.echo("")
    utils.echo("Done.")


if __name__ == "__main__":
    # Get an AWS profile.
    aws_profile = profile.configured()

    # Set some parameters.
    load_balancer = "joe-loadbalancer"
    availability_zones = None  # ["us-east-1c", "us-east-1e"]
    vpc_id = "vpc-8c65bce8"  # None

    # Delete the load balancer.
    params = {}
    params["aws_profile"] = aws_profile
    params["load_balancer"] = load_balancer
    delete_load_balancer(**params)
    utils.exit()
    
    # Create the load balancer.
    params = {}
    params["aws_profile"] = aws_profile
    params["name"] = load_balancer
    params["vpc_id"] = vpc_id
    params["availability_zones"] = availability_zones
    create_load_balancer(**params)

