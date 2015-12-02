# -*- coding: utf-8 -*-

"""For creating and managing VPCs."""

from polarexpress.aws import availabilityzone
from polarexpress.aws import internetgateway
from polarexpress.aws import profile
from polarexpress.aws import routetable
from polarexpress.aws import securitygroup
from polarexpress.aws import subnet
from polarexpress.aws import vpc

from polarexpress.tasks import utils


def create_vpc(
        aws_profile,
        vpc_name,
        vpc_cidr_block,
        subnet_cidr_blocks,
        security_group_cidr_block,
        region="us-east-1"):
    """Create a public facing VPC."""
    utils.heading("Creating VPC")
    response = vpc.create(profile=aws_profile, cidr_block=vpc_cidr_block)
    utils.echo_data(response)
    vpc_id = response["Vpc"]["VpcId"]
    utils.emphasize("VPC ID: " + str(vpc_id))

    # Tag the VPC with a name.
    utils.heading("Tagging VPC with the name '" + str(vpc_name) + "'")
    response = vpc.tag(
        profile=aws_profile,
        vpc=vpc_id,
        key="Name",
        value=vpc_name)
    utils.echo_data(response)
    utils.emphasize("TAG NAME: Name")
    utils.emphasize("TAG VALUE: " + str(vpc_name))

    # Create an internet gateway.
    utils.heading("Creating internet gateway")
    response = internetgateway.create(profile=aws_profile)
    gateway_id = response["InternetGateway"]["InternetGatewayId"]
    utils.emphasize("GATEWAY ID: " + str(gateway_id))

    # Attach it to the VPC.
    utils.heading("Attaching internet gateway to VPC")
    response = vpc.attach_internet_gateway(aws_profile, vpc_id, gateway_id)
    utils.echo_data(response)

    # Create the specified subnets.
    utils.heading("Creating subnets")
    for zone_name, subnet_cidr_block in subnet_cidr_blocks.items():
        response = subnet.create(
            profile=aws_profile,
            cidr_block=subnet_cidr_block,
            vpc=vpc_id,
            availability_zone=zone_name)
        utils.echo_data(response)

    # Get a list of the subnet IDS
    utils.heading("Getting subnet IDs")
    response = subnet.get(profile=aws_profile)
    utils.echo_data(response)
    all_subnets = response["Subnets"]
    subnet_ids = [x["SubnetId"] for x in all_subnets if x["VpcId"] == vpc_id]
    utils.emphasize("SUBNET IDs: " + str(subnet_ids))

    # Create a route table.
    utils.heading("Creating route table")
    response = routetable.create(
        profile=aws_profile,
        vpc=vpc_id)
    utils.echo_data(response)
    routetable_id = response["RouteTable"]["RouteTableId"]
    utils.emphasize("ROUTE TABLE ID: " + str(routetable_id))
    
    # Add a route for the internet gateway.
    utils.heading("Adding a route for the internet gateway")
    response = routetable.add_route(
        profile=aws_profile,
        route_table=routetable_id,
        cidr_block="0.0.0.0/0",
        gateway=gateway_id)
    utils.echo_data(response)
    
    # Associate the route table with subnets.
    utils.heading("Associating the route table with subnets")
    for subnet_id in subnet_ids:
        response = routetable.associate_subnet(
            profile=aws_profile,
            route_table=routetable_id,
            subnet=subnet_id)
        utils.echo_data(response)

    # Create a security group.
    utils.heading("Creating security group")
    response = securitygroup.create(
        profile=aws_profile,
        name=vpc_name + "--security-group",
        vpc=vpc_id)
    utils.echo_data(response)
    securitygroup_id = response["GroupId"]
    utils.emphasize("SECURITY GROUP ID: " + str(securitygroup_id))

    # Allow inbound traffic to port 80.
    cidr_block_str = str(security_group_cidr_block)
    utils.heading("Allowing inbound TCP 80:80 from " + cidr_block_str)
    response = securitygroup.add_inbound_rule(
        profile=aws_profile,
        security_group=securitygroup_id,
        protocol="tcp",
        from_port=80,
        to_port=80,
        cidr_block=security_group_cidr_block)
    utils.echo_data(response)

    utils.heading("Allowing inbound TCP 22:22 from " + cidr_block_str)
    response = securitygroup.add_inbound_rule(
        profile=aws_profile,
        security_group=securitygroup_id,
        protocol="tcp",
        from_port=22,
        to_port=22,
        cidr_block=security_group_cidr_block)
    utils.echo_data(response)

    utils.heading("Allowing inbound TCP 3306:3306 from " + cidr_block_str)
    response = securitygroup.add_inbound_rule(
        profile=aws_profile,
        security_group=securitygroup_id,
        protocol="tcp",
        from_port=3306,
        to_port=3306,
        cidr_block=security_group_cidr_block)
    utils.echo_data(response)

    utils.heading("Allowing inbound TCP 443:443 from " + cidr_block_str)
    response = securitygroup.add_inbound_rule(
        profile=aws_profile,
        security_group=securitygroup_id,
        protocol="tcp",
        from_port=443,
        to_port=443,
        cidr_block=security_group_cidr_block)
    utils.echo_data(response)

    # Exit nicely.
    utils.echo("Done.")


if __name__ == "__main__":
    aws_profile = profile.configured()
    create_vpc(aws_profile, "joe-vpc", "10.0.0.0/16", subnet_cidr_blocks={"us-east-1a": "10.0.1.0/24", "us-east-1b": "10.0.2.0/24"}, security_group_cidr_block="0.0.0.0/0")

