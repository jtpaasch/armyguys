# -*- coding: utf-8 -*-

"""Jobs for tagging security groups."""

from ...aws import securitygroup


def tag(profile, security_group, key, value):
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
