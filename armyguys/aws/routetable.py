# -*- coding: utf-8 -*-

"""Utilities for working with route tables."""

from . import client as boto3client


def create(profile, vpc):
    """Create a route table for a VPC.

    Args:

        profile
            A profile to connect to AWS with.

        vpc
            The ID of a VPC.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("ec2", profile)
    params = {}
    params["VpcId"] = vpc
    return client.create_route_table(**params)


def delete(profile, route_table):
    """Delete a route table from a VPC.

    Args:

        profile
            A profile to connect to AWS with.

        route_table
            The ID of the route table you want to delete.

    """
    client = boto3client.get("ec2", profile)
    params = {}
    params["RouteTableId"] = vpc
    return client.delete_route_table(**params)


def get(profile):
    """Get a list of all route tables.

    Args:

        profile
            A profile to connect to AWS with.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("ec2", profile)
    return client.describe_route_tables()


def add_route(profile, route_table, cidr_block, gateway):
    """Create a route to a route table.

    Args:

        profile
            A profile to connect to AWS with.

        route_table
            The ID of the table you want to add a route to.

        cidr_block
            The range of destinations the rule applies to, in CIDR
            notation, e.g., "10.0.0.0/16".

        gateway
            The ID of the internet gateway.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("ec2", profile)
    params = {}
    params["RouteTableId"] = route_table
    params["DestinationCidrBlock"] = cidr_block
    params["GatewayId"] = gateway
    return client.create_route(**params)


def remove_route(profile, route_table, cidr_block):
    """Delete a route from a route table.

    Args:

        profile
            A profile to connect to AWS with.

        route_table
            The ID of the table you want to remove the route from.

        cidr_block
            The range of destinations the route applies to, in CIDR
            notation, e.g., "10.0.0.0/16".

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("ec2", profile)
    params = {}
    params["RouteTableId"] = route_table
    params["DestinationCidrBlock"] = cidr_block
    return client.delete_route(**params)


def associate_subnet(profile, route_table, subnet):
    """Associate a subnet with a route table.

    Args:

        profile
            A profile to connect to AWS with.

        route_table
            The ID of a route table.

        subnet
            The ID of a subnet.

    Returns:
       The JSON response returned by boto3.

    """
    client = boto3client.get("ec2", profile)
    params = {}
    params["RouteTableId"] = route_table
    params["SubnetId"] = subnet
    return client.associate_route_table(**params)


def disassociate_subnet(profile, association):
    """Dissaciate a subnet from a route table.

    Args:

        profile
            A profile to connect to AWS with.

        association
            The ID of the association to remove.

    """
    client = boto3client.get("ec2", profile)
    params = {}
    params["AssociationId"] = association
    return client.disassociate_route_table(**params)
