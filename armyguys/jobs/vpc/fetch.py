# -*- coding: utf-8 -*-

"""Utilities for fetching VPC info."""

from ...aws import vpc


def get_default_vpc(profile):
    """Get the default VPC.

    Args:

        profile
            A profile to connect to AWS with.

    Return:
        The data for the VPC returned by AWS,
        or None if no default VPC was found.

    """
    params = {}
    params["profile"] = profile
    params["filters"] = [{"Name": "isDefault", "Values": ["true"]}]
    response = vpc.get(**params)
    data = response.get("Vpcs")
    result = None
    if len(data) == 1:
        result = data[0]
    return result


def get_all(profile):
    """Get all VPCs.

    Args:

        profile
            A profile to connect to AWS with.

    Return:
        The data returned by AWS, or None if no VPCs were found.

    """
    params = {}
    params["profile"] = profile
    response = vpc.get(**params)
    data = response.get("Vpcs")
    result = None
    if len(response) > 0:
        result = data
    return result


def get_by_ID(profile, ID):
    """Get a VPC by ID.

    Args:

        profile
            A profile to connect to AWS with.

        ID
            The ID of the VPC.

    Return:
        The data returned by AWS, or None if none were found.

    """
    params = {}
    params["profile"] = profile
    params["filters"] = [{"Name": "vpc-id", "Values": [ID]}]
    response = vpc.get(**params)
    data = response.get("Vpcs")
    result = None
    if len(data) > 1:
        raise Exception("Too many records returned.")
    elif len(data) > 0:
        result = data[0]
        return result
