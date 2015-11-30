# -*- coding: utf-8 -*-

"""Utilities for working with ECS tasks."""

from .. import client as boto3client


def create(profile, cluster, task_definition):
    """Run a task in a cluster.

    Args:

        profile
            A profile to connect to AWS with.

        cluster
            The name of the cluster to run the task in.

        task_definition
            The full name of the task to run, i.e., family:revision.

    Returns:
        The data returned by boto3.

    """
    client = boto3client.get("ecs", profile)
    params = {}
    params["cluster"] = cluster
    params["taskDefinition"] = task_definition
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


def get(profile, cluster, task=None):
    """Get all ECS tasks in a cluster, or a specific one.

    Args:

        profile
            A profile to connect to AWS with.

        cluster
            The name of a cluster.

        task
            The ID or Amazon ARN you want to get. If this is omitted,
            all tasks are returned.

    Returns:
        The data returned by boto3.

    """
    client = boto3client.get("ecs", profile)
    if task:
        task_arns = [task]
    else:
        params = {}
        params["cluster"] = cluster
        tasks = client.list_tasks(**params)
        task_arns = tasks["taskArns"]
    params = {}
    params["cluster"] = cluster
    params["tasks"] = task_arns
    return client.describe_tasks(**params)
