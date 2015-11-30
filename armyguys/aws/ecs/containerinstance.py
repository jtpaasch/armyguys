# -*- coding: utf-8 -*-

"""Utilities for working with ECS container instances."""

from .. import client as boto3client


def get(profile, cluster):
    """Get a list of all ECS tasks in a cluster.

    Args:

        profile
            A profile to connect to AWS with.

        cluster
            The name of a cluster.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("ecs", profile)
    params = {}
    params["cluster"] = cluster
    response = client.list_container_instances(**params)
    instance_arns = response["containerInstanceArns"]
    result = None
    if instance_arns:
        params = {}
        params["cluster"] = cluster
        params["containerInstances"] = instance_arns
        result = client.describe_container_instances(**params)
    return result
