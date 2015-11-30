# -*- coding: utf-8 -*-

"""Utilities for working with ECS services."""

from .. import client as boto3client


def create(profile, name, cluster, task_definition,
           count=1, load_balancers=None, role=None):
    """Create a service in a cluster.

    Args:

        profile
            A profile to connect to AWS with.

        name
            A name to give to the service.

        cluster
            The name of the cluster to start the service in.

        task_definition
            The full name of the task to run, i.e., family:revision.

        count
            The number of instances of the service to run in parallel.

        load_balancers
            A list of load balancer dicts.

        role
            A role to give the service.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("ecs", profile)
    params = {}
    params["serviceName"] = name
    params["taskDefinition"] = task_definition
    params["cluster"] = cluster
    params["desiredCount"] = count
    if load_balancers:
        params["loadBalancers"] = load_balancers
    if role:
        params["role"] = role
    return client.create_service(**params)


def update(profile, service, cluster, task_definition=None, count=None):
    """Update a service with a new task definition or count.

    Args:

        profile
            A profile to connect to AWS with.

        service
            The name of the service to update.

        cluster
            The name of the cluster the service is running in.

        task_definition
            The full name of the task to run, i.e., family:revision.
            If None, no change is made to the task definition.

        count
            The number of instances of the service to run in parallel.
            If None, no change is made to the count.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("ecs", profile)
    params = {}
    params["service"] = service
    params["cluster"] = cluster
    if task_definition:
        params["taskDefinition"] = task_definition
    if count or count == 0:
        params["desiredCount"] = count
    return client.update_service(**params)


def delete(profile, service, cluster):
    """Stop a service in a cluster.

    Args:

        profile
            A profile to connect to AWS with.

        service
            The name of the service to stop.

        cluster
            The name of the cluster to stop the service in.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("ecs", profile)
    params = {}
    params["service"] = service
    params["cluster"] = cluster
    return client.delete_service(**params)


def get(profile, cluster, service=None):
    """Get a list of all ECS services in a cluster.

    Args:

        profile
            A profile to connect to AWS with.

        cluster
            The name of a cluster.

        service
            The name of a service to get. If ommitted,
            all services in the cluster are returned.


    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("ecs", profile)
    if service:
        service_arns = [service]
    else:
        params = {}
        params["cluster"] = cluster
        services = client.list_services(**params)
        service_arns = services["serviceArns"]
    result = []
    if service_arns:
        params = {}
        params["cluster"] = cluster
        params["services"] = service_arns
        result = client.describe_services(**params)
    return result
