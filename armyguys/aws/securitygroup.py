# -*- coding: utf-8 -*-

"""Utilities for working with EC2 security groups."""

from os import path
from . import client as boto3client


def create(profile, name, vpc=None):
    """Create a security group.  

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name to give to the security group.

        vpc
            The VPC ID to put the security group in.
            If none is specified, the default VPC is used.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("ec2", profile)
    params = {}
    params["GroupName"] = name
    params["Description"] = name
    if vpc:
        params["VpcId"] = vpc
    return client.create_security_group(**params)


def delete(profile, group_id):
    """Delete a security group.

    Args:

        profile
            A profile to connect to AWS with.

        group_id
            The ID of the group you want to delete.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("ec2", profile)
    params = {}
    params["GroupId"] = group_id
    return client.delete_security_group(**params)


def get(profile, security_group):
    """Get a list of security groups.

    Args:

        profile
            A profile to connect to AWS with.

        security_group
            The name of a security group to get.
            If this is omitted, all security groups are returned.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("ec2", profile)
    params = {}
    if security_group:
        params["Filters"] = [{
            "Name": "group-name",
            "Values": [security_group],
        }]
    return client.describe_security_groups(**params)


def tag(profile, security_group, key, value):
    """Add a tag to a security group.

    Args:

        profile
            A profile to connect to AWS with.

        security_group
            The ID of the security group you want to tag.

        key
            The key/name of the tag.

        value
            The value of the tag.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("ec2", profile)
    params = {}
    params["Resources"] = [security_group]
    params["Tags"] = [{"Key": key, "Value": value}]
    return client.create_tags(**params)


def add_inbound_rule(profile,
                     security_group,
                     protocol,
                     from_port,
                     to_port,
                     cidr_block):
    """Create a rule for inbound traffic in a security group.

    Args:

        profile
            A profile to connect to AWS with.

        security_group
            The ID of the security group to add the rule to.

        protocol
            The protocol to allow inbound traffic to connect with.
            Can be ``tcp``, ``udp``, ``icmp``, or a Number. -1 is all.

        from_port
            The port to accept incoming connections from.

        to_port
            The port to accept incoming connections to.

        cidr_block
            The IP range (as a CIDR block) to accept connections from.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("ec2", profile)
    params = {}
    params["GroupId"] = security_group
    params["IpPermissions"] = [{
        "IpProtocol": protocol,
        "FromPort": from_port,
        "ToPort": to_port,
        "IpRanges": [{"CidrIp": cidr_block}],
        }]
    return client.authorize_security_group_ingress(**params)


def remove_inbound_rule(profile,
                        security_group,
                        protocol,
                        from_port,
                        to_port,
                        cidr_block):
    """Delete a rule for inbound traffic in a security group.

    Args:

        profile
            A profile to connect to AWS with.

        security_group
            The ID of the security group to delete the rule from.

        protocol
            The protocol the rule allows.

        from_port
            The port the rule allows connections from.

        to_port
            The port the rule allows connections to.

        cidr_block
            The IP range (as a CIDR block) the rule allows connections from.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("ec2", profile)
    params = {}
    params["GroupId"] = security_group
    params["IpPermissions"] = [{
        "IpProtocol": protocol,
        "FromPort": from_port,
        "ToPort": to_port,
        "IpRanges": [{"CidrIp": cidr_block}],
        }]
    return client.revoke_security_group_ingress(**params)


def add_outbound_rule(profile,
                      security_group,
                      protocol,
                      from_port,
                      to_port,
                      cidr_block):
    """Create a rule for outbound traffic in a security group.

    Args:

        profile
            A profile to connect to AWS with.

        security_group
            The ID of the security group to add the rule to.

        protocol
            The protocol to allow outbound traffic to use.
            Can be ``tcp``, ``udp``, ``icmp``, or a Number. -1 is all.

        from_port
            The port to allow outbound connections to go out on.

        to_port
            The port to allow outbound connections to go out to.

        cidr_block
            The IP range (as a CIDR block) to allow connections to.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("ec2", profile)
    params = {}
    params["GroupId"] = security_group
    params["IpPermissions"] = [{
        "IpProtocol": protocol,
        "FromPort": from_port,
        "ToPort": to_port,
        "IpRanges": [{"CidrIp": cidr_block}],
        }]
    return client.authorize_security_group_egress(**params)


def remove_outbound_rule(profile,
                         security_group,
                         protocol,
                         from_port,
                         to_port,
                         cidr_block):
    """Delete a rule for outbound traffic in a security group.

    Args:

        profile
            A profile to connect to AWS with.

        security_group
            The ID of the security group to delete the rule from.

        protocol
            The protocol the rule allows.

        from_port
            The port the rule allows connections from.

        to_port
            The port the rule allows connections to.

        cidr_block
            The IP range (as a CIDR block) the rule allows connections to.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("ec2", profile)
    params = {}
    params["GroupId"] = security_group
    params["IpPermissions"] = [{
        "IpProtocol": protocol,
        "FromPort": from_port,
        "ToPort": to_port,
        "IpRanges": [{"CidrIp": cidr_block}],
        }]
    return client.revoke_security_group_egress(**params)
