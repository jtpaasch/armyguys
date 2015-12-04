# -*- coding: utf-8 -*-

"""Utilities for fetching subnet info."""

from ...aws import subnet


def get_all(profile):
    """Get all subnets.

    Args:

        profile
            A profile to connect to AWS with.

    Return:
        The data returned by AWS, or None if no subnets were found.

    """
    params = {}
    params["profile"] = profile
    response = subnet.get(**params)
    data = response.get("Subnets")
    result = None
    if len(data) > 0:
        result = data
    return result


def get_all_in_vpc(profile, vpc_id):
    """Get all subnets in a VPC.

    Args:

        profile
            A profile to connect to AWS with.

        vpc_id
            The VPC to find subnets in.

    Return:
        The data returned by AWS, or None if no subnets were found.

    """
    params = {}
    params["profile"] = profile
    params["filters"] = [{"Name": "vpc-id", "Values": [vpc_id]}]
    response = subnet.get(**params)
    data = response.get("Subnets")
    result = None
    if len(data) > 0:
        result = data
    return result
