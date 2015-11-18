# -*- coding: utf-8 -*-

"""Utilities for working with VPCs."""

from . import client as boto3client


def create(profile, cidr_block):
    """Create a VPC:.

    Args:

        profile
            A profile to connect to AWS with.

        cidr_block
            The network range of the VPC, in CIDR notation,
            e.g., "10.0.0.0/16".

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("ec2", profile)
    params = {}
    params["CidrBlock"] = cidr_block
    return client.create_vpc(**params)


def delete(profile, vpc):
    """Delete a VPC.

    Args:

        profile
            A profile to connect to AWS with.

        vpc
            The ID of the VPC you want to delete.

    """
    client = boto3client.get("ec2", profile)
    params = {}
    params["VpcId"] = vpc
    return client.delete_vpc(**params)


def get(profile):
    """Get a list of all VPCs.

    Args:

        profile
            A profile to connect to AWS with.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("ec2", profile)
    return client.describe_vpcs()


def tag(profile, vpc, key, value):
    """Add a tag to a VPC.

    Args:

        profile
            A profile to connect to AWS with.

        vpc
            The ID of the VPC you want to tag.

        key
            The key/name of the tag.

        value
            The value of the tag.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("ec2", profile)
    params = {}
    params["Resources"] = [vpc]
    params["Tags"] = [{"Key": key, "Value": value}]
    return client.create_tags(**params)


def attach_internet_gateway(profile, vpc, gateway):
    """Attach an internet gateway to a VPC.

    Args:

        profile
            A profile to connect to AWS with.

        vpc
            The ID of the VPC you want to attach the gateway to.

        gateway
            The ID of the gateway.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("ec2", profile)
    params = {}
    params["VpcId"] = vpc
    params["InternetGatewayId"] = gateway
    return client.attach_internet_gateway(**params)


def detach_internet_gateway(profile, vpc, gateway):
    """Detach an internet gateway from a VPC.

    Args:

        profile
            A profile to connect to AWS with.

        vpc
            The ID of the VPC you want to detach the gateway from.

        gateway
            The ID of the gateway.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("ec2", profile)
    params = {}
    params["VpcId"] = vpc
    params["InternetGatewayId"] = gateway
    return client.detach_internet_gateway(**params)


def enable_dns_support(profile, vpc):
    """Enable DNS support for a VPC.

    Args:

        profile
            A profile to connect to AWS with.

        vpc
            The ID of the VPC you want to enable DNS support for.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("ec2", profile)
    params = {}
    params["VpcId"] = vpc
    params["EnableDnsSupport"] = {"Value": True}
    return client.modify_vpc_attribute(**params)


def disable_dns_support(profile, vpc):
    """Disable DNS support for a VPC.

    Args:

        profile
            A profile to connect to AWS with.

        vpc
            The ID of the VPC you want to disable DNS support for.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("ec2", profile)
    params = {}
    params["VpcId"] = vpc
    params["EnableDnsSupport"] = {"Value": False}
    return client.modify_vpc_attribute(**params)


def enable_dns_hostnames(profile, vpc):
    """Enable DNS hostnames for instances in a VPC.

    Args:

        profile
            A profile to connect to AWS with.

        vpc
            The ID of the VPC you want to enable DNS hostnames for.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("ec2", profile)
    params = {}
    params["VpcId"] = vpc
    params["EnableDnsHostnames"] = {"Value": True}
    return client.modify_vpc_attribute(**params)


def disable_dns_hostnames(profile, vpc):
    """Disable DNS hostnames for instances in a VPC.

    Args:

        profile
            A profile to connect to AWS with.

        vpc
            The ID of the VPC you want to disable DNS hostnames for.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("ec2", profile)
    params = {}
    params["VpcId"] = vpc
    params["EnableDnsHostnames"] = {"Value": False}
    return client.modify_vpc_attribute(**params)
