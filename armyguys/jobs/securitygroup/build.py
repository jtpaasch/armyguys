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


def tag(profile, security_group, key=None, value=None):
    """Tag a security group.

    Args:

        profile
            A profile to connect to AWS with.

        security_group
            The name of the group you want to tag.

        key
            The key you want to give to the tag.

        value
            The value you want to give to the tag.

    Return:
        The data returned by AWS.

    """
    params = {}
    params["profile"] = profile
    params["security_group"] = security_group
    params["key"] = key
    params["value"] = value
    return securitygroup.tag(**params)
