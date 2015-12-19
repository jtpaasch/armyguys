# -*- coding: utf-8 -*-

"""Utilities for working with VPC subnets."""

from . import client as boto3client


def create(profile, cidr_block, vpc, availability_zone=None):
    """Create a subnet in a VPC.

    Args:

        profile
            A profile to connect to AWS with.

        cidr_block
            The network range for the subnet, in CIDR notation.
            For instance, "10.0.0.0/24".

        vpc
            The ID of the VPC you want to create the subnet in.

        availability_zone
            The name of the availability zone to create the subnet in.
            If None, Amazon will pick one for you.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("ec2", profile)
    params = {}
    params["CidrBlock"] = cidr_block
    params["VpcId"] = vpc
    if availability_zone:
        params["AvailabilityZone"] = availability_zone
    return client.create_subnet(**params)


def delete(profile, subnet):
    """Delete a subnet from a VPC.

    Args:

        profile
            A profile to connect to AWS with.

        subnet
            The ID of the subnet you want to delete.

    """
    client = boto3client.get("ec2", profile)
    params = {}
    params["SubnetId"] = subnet
    return client.delete_subnet(**params)


def get(profile, filters=None):
    """Get a list of all subnets.

    Args:

        profile
            A profile to connect to AWS with.

        filters
            Filters to apply to the request.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("ec2", profile)
    params = {}
    if filters:
        params["Filters"] = filters
    return client.describe_subnets(**params)


def enable_public_ips(profile, subnet):
    """Set the subnet to give instances public IPs by default.

    Args:

        profile
            A profile to connect to AWS with.

        subnet
            The ID of the subnet.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("ec2", profile)
    params = {}
    params["SubnetId"] = subnet
    params["MapPublicIpOnLaunch"] = {"Value": True}
    return client.modify_subnet_attribute(**params)


def disable_public_ips(profile, subnet):
    """Set the subnet not to give instances public IPs by default.

    Args:

        profile
            A profile to connect to AWS with.

        subnet
            The ID of the subnet.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("ec2", profile)
    params = {}
    params["SubnetId"] = subnet
    params["MapPublicIpOnLaunch"] = {"Value": False}
    return client.modify_subnet_attribute(**params)


def tag(profile, subnet, key, value):
    """Add a tag to a subnet.

    Args:

        profile
            A profile to connect to AWS with.

        subnet
            The ID of the subnet you want to tag.

        key
            The key/name of the tag.

        value
            The value of the tag.

    Returns:
        The response returned by boto3.

    """
    client = boto3client.get("ec2", profile)
    params = {}
    params["Resources"] = [subnet]
    params["Tags"] = [{"Key": key, "Value": value}]
    return client.create_tags(**params)
