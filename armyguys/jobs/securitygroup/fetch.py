# -*- coding: utf-8 -*-

"""Jobs for fetching security group data."""

from ...aws import securitygroup


def get_all(profile):
    """Get all security groups.

    Args:

        profile
            A profile to connect to AWS with.

    Return:
        The data returned by AWS, or None if none were found.

    """
    params = {}
    params["profile"] = profile
    response = securitygroup.get(**params)
    data = response.get("SecurityGroups")
    result = None
    if len(data) > 0:
        result = data
    return result


def get_all_in_vpc(profile, vpc_id):
    """Get all security groups in a VPC.

    Args:

        profile
            A profile to connect to AWS with.

        vpc_id
            The VPC to find security groups in.

    Return:
        The data returned by AWS, or None if none were found.

    """
    params = {}
    params["profile"] = profile
    params["filters"] = [{"Name": "vpc-id", "Values": [vpc_id]}]
    response = securitygroup.get(**params)
    data = response.get("SecurityGroups")
    result = None
    if len(data) > 0:
        result = data
    return result


def get_by_name(profile, name):
    """Get a security groups by name.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name of the security group.

    Return:
        The data returned by AWS, or None if none were found.

    """
    params = {}
    params["profile"] = profile
    params["filters"] = [{"Name": "group-name", "Values": [name]}]
    response = securitygroup.get(**params)
    data = response.get("SecurityGroups")
    result = None
    if len(data) > 1:
        raise Exception("Too many records returned.")
    elif len(data) > 0:
        result = data[0]
    return result
