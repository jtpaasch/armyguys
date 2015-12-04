# -*- coding: utf-8 -*-

"""Jobs for creating load balancers."""

from ...aws import loadbalancer


def create(profile):
    """Create a load balancer.

    Args:

        profile
            A profile to connect to AWS with.

    Return:
        The data returned by AWS, or None if none were found.

    """
    params = {}
    params["profile"] = profile
    response = loadbalancer.create(**params)
    data = response.get("LoadBalancerDescriptions")
    result = None
    if len(data) > 0:
        result = data
    return result
