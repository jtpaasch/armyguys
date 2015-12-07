# -*- coding: utf-8 -*-

"""Jobs for deleting security groups."""

from ...aws import securitygroup


def delete(profile, security_group):
    """Delete a security group.

    Args:

        profile
            A profile to connect to AWS with.

        security_group
            The ID of the security group you want to delete.

    Return:
        The data returned by AWS.

    """
    params = {}
    params["profile"] = profile
    params["security_group"] = security_group
    return securitygroup.delete(**params)


def try_to_delete(profile, security_group, max_attempts=25, wait_interval=5):
    """Delete a security group.

    Args:

        profile
            A profile to connect to AWS with.

        security_group
            The ID of the security group you want to delete.

        max_attempts
            The max number of times to try to delete the security group.

        wait_internal
            How many seconds to wait in between each attempt.

    Return:
        Boolean for success.

    """
    params = {}
    params["profile"] = profile
    params["security_group"] = security_group
    params["max_attempts"] = max_attempts
    params["wait_interval"] = wait_interval
    return securitygroup.try_to_delete(**params)
