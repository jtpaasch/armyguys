# -*- coding: utf-8 -*-

"""Jobs for creating security groups."""

from ...aws import securitygroup


def create(profile, name, vpc=None):
    """Create a security group.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name you want to give to the security group.

        vpc
            The ID of a VPC you want to create the group in.

    Return:
        The data returned by AWS, or None if none were found.

    """
    params = {}
    params["profile"] = profile
    params["name"] = name
    if vpc:
        params["vpc"] = vpc
    return securitygroup.create(**params)
