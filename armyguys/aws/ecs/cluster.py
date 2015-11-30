# -*- coding: utf-8 -*-

"""Utilities for working with ECS clusters."""

from .. import client as boto3client


def create(profile, name):
    """Create an ECS cluster.

    Args:

        profile
            A profile to connect to AWS with.

        name
            A name to give to the cluster.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("ecs", profile)
    params = {}
    params["clusterName"] = name
    return client.create_cluster(**params)


def delete(profile, cluster):
    """Delete an ECS cluster.

    Args:

        profile
            A profile to connect to AWS with.

        cluster
            The name of the cluster to delete.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("ecs", profile)
    params = {}
    params["cluster"] = cluster
    return client.delete_cluster(**params)


def get(profile, cluster=None):
    """Get all ECS clusters, or a specific one.

    Args:

        profile
            A profile to connect to AWS with.

        cluster
            The name of a cluster to get. If this is
            omitted, all clusters are returned.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("ecs", profile)
    if cluster:
        cluster_arns = [cluster]
    else:
        clusters = client.list_clusters()
        cluster_arns = clusters["clusterArns"]
    params = {}
    params["clusters"] = cluster_arns
    return client.describe_clusters(**params)
