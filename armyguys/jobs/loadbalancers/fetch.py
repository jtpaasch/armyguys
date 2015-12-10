# -*- coding: utf-8 -*-

"""Jobs for fetching load balancer info."""

from ...aws import loadbalancer


def get_all(profile):
    """Get all load balancers.

    Args:

        profile
            A profile to connect to AWS with.

    Return:
        The data returned by AWS, or None if none were found.

    """
    params = {}
    params["profile"] = profile
    response = loadbalancer.get(**params)
    data = response.get("LoadBalancerDescriptions")
    result = None
    if len(data) > 0:
        result = data
    return result


def get_all_in_vpc(profile, vpc_id):
    """Get all load balancers in a VPC.

    Args:

        profile
            A profile to connect to AWS with.

        vpc_id
            The VPC to find load balancers in.

    Return:
        The data returned by AWS, or None if none were found.

    """
    params = {}
    params["profile"] = profile
    response = loadbalancer.get(**params)
    data = response.get("LoadBalancerDescriptions")
    result = None
    if len(data) > 0:
        matches = [x for x in data if x["VPCId"] == vpc_id]
        if matches:
            result = matches
    return result


def get_by_name(profile, name):
    """Get a load balancer by name.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name of the load balancer.

    Return:
        The data returned by AWS, or None if none were found.

    """
    params = {}
    params["profile"] = profile
    response = loadbalancer.get(**params)
    data = response.get("LoadBalancerDescriptions")
    result = None
    if len(data) > 0:
        matches = [x for x in data if x["LoadBalancerName"] == name]
        if matches:
            if len(matches) > 1:
                raise Exception("Too many records returned.")
            elif len(matches) > 0:
                result = matches[0]
    return result
