# -*- coding: utf-8 -*-

"""Utilities for working with ECS clusters."""

import json
from . import client as boto3client


def create_cluster(profile, name):
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


def delete_cluster(profile, name):
    """Delete an ECS cluster.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name of the cluster to delete.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("ecs", profile)
    params = {}
    params["cluster"] = name
    return client.delete_cluster(**params)


def upload_task_definition(profile, filepath):
    """Upload a task definition to ECS.

    Args:

        profile
            A profile to connect to AWS with.

        filepath
            The path to a task definition *.json file.

    Returns:
        The JSON response returned by boto3.

    """
    with open(filepath) as f:
        data = json.load(f)
    client = boto3client.get("ecs", profile)
    params = {}
    params["family"] = data.get("family")
    params["containerDefinitions"] = data.get("containerDefinitions")
    params["volumes"] = data.get("volumes")
    return client.register_task_definition(**params)


def delete_task_definition(profile, name):
    """Delete an ECS task definition.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The full name, i.e., family:revision.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("ecs", profile)
    params = {}
    params["taskDefinition"] = name
    return client.deregister_task_definition(**params)


def run_task(profile, cluster, task_definition):
    """Run a task in a cluster.

    Args:

        profile
            A profile to connect to AWS with.

        cluster
            The name of the cluster to run the task in.

        task_definition
            The full name of the task to run, i.e., family:revision.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("ecs", profile)
    params = {}
    params["cluster"] = cluster
    params["taskDefinition"] = task_definition
    return client.run_task(**params)


def stop_task(profile, cluster, task_id):
    """Stop a task in a cluster.

    Args:

        profile
            A profile to connect to AWS with.

        cluster
            The name of the cluster the task is running in.

        task_id
            The ID of the task to stop.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("ecs", profile)
    params = {}
    params["cluster"] = cluster
    params["task"] = task_id
    return client.stop_task(**params)


def start_service(profile, name, cluster, task_definition,
                  count=1, load_balancers=None, role=None):
    """Create a service in a cluster.

    Args:

        profile
            A profile to connect to AWS with.

        name
            A name to give to the task.

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


def update_service(profile, service, cluster, task_definition=None,
                   count=None):
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


def stop_service(profile, service, cluster):
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
