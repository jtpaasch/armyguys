# -*- coding: utf-8 -*-

"""Jobs for deleting load balancers."""

from ...aws import loadbalancer


def delete(profile, load_balancer):
    """Delete a load balancer.

    Args:

        profile
            A profile to connect to AWS with.

        load_balancer
            The name of the load balancer you want to delete.

    Return:
        The data returned by AWS.

    """
    params = {}
    params["profile"] = profile
    params["load_balancer"] = load_balancer
    return loadbalancer.delete(**params)
