# -*- coding: utf-8 -*-

"""Utilities for working with ECS tasks."""

from .. import client as boto3client


def create(profile, cluster, task_definition, started_by=None, count=None):
    """Run a task in a cluster.

    Args:

        profile
            A profile to connect to AWS with.

        cluster
            The name of the cluster to run the task in.

        task_definition
            The full name of the task to run, i.e., family:revision.

        started_by
            A string to help identify the task later.

        count
            The number of copies of the task to run.

    Returns:
        The data returned by boto3.

    """
    client = boto3client.get("ecs", profile)
    params = {}
    params["cluster"] = cluster
    params["taskDefinition"] = task_definition
    if started_by:
        params["startedBy"] = started_by
    if count:
        params["count"] = count
    return client.run_task(**params)


def delete(profile, cluster, task_id):
    """Stop a task in a cluster.

    Args:

        profile
            A profile to connect to AWS with.

        cluster
            The name of the cluster the task is running in.

        task_id
            The ID of the task to stop.

    Returns:
        The data returned by boto3.

    """
    client = boto3client.get("ecs", profile)
    params = {}
    params["cluster"] = cluster
    params["task"] = task_id
    return client.stop_task(**params)


def get_arns(profile, cluster, started_by=None):
    """Get all ECS task ARNs for a cluster.

    Args:

        profile
            A profile to connect to AWS with.

        cluster
            The name of a cluster.

        started_by
            Get tasks started with this value.

    Returns:
        The data returned by boto3.

    """
    result = None
    client = boto3client.get("ecs", profile)
    params = {}
    params["cluster"] = cluster
    if started_by:
        params["startedBy"] = started_by
    return client.list_tasks(**params)


def get(profile, cluster, tasks):
    """Get the info for tasks in a cluster.

    Args:

        profile
            A profile to connect to AWS with.

        cluster
            The name of a cluster.

        tasks
            The list of task ARNs to fetch.

    Returns:
        The data returned by boto3.

    """
    client = boto3client.get("ecs", profile)
    params = {}
    params["cluster"] = cluster
    params["tasks"] = tasks
    return client.describe_tasks(**params)
