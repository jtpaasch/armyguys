# -*- coding: utf-8 -*-

"""Jobs for creating load balancers."""

from ...aws import loadbalancer


def create(profile, name, listeners, subnets=None, availability_zones=None, security_groups=None):
    """Create a load balancer.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name you want to give to the load balancer.

        listeners
            A dictionary of listeners for the load balancer.

        subnets
            A list of subnet IDs to launch the load balancer into (VPC only).

        availability_zones
            Or, a list of availability zone names.

        security_groups
            A list of security group IDs for the load balancer (VPC only).

    Return:
        The data returned by AWS.

    """
    params = {}
    params["profile"] = profile
    params["name"] = name
    params["listeners"] = listeners
    if subnets:
        params["subnets"] = subnets
    elif availability_zones:
        params["availability_zones"] = availability_zones
    if security_groups:
        params["security_groups"] = security_groups
    return loadbalancer.create(**params)


def tag(profile, load_balancer, key, value):
    """Tag a load balancer.

    Args:

        profile
            A profile to connect to AWS with.

        load_balancer
            The name of the load balancer you want to tag.

        key
            The key you want to give to the tag.

        value
            The value you want to give to the tag.

    Return:
        The data returned by AWS.

    """
    params = {}
    params["profile"] = profile
    params["load_balancer"] = load_balancer
    params["key"] = key
    params["value"] = value
    return loadbalancer.tag(**params)
