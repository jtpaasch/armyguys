# -*- coding: utf-8 -*-

"""Jobs for ECS tasks."""

import os

from ..aws.ecs import task

from .exceptions import FileDoesNotExist
from .exceptions import ImproperlyConfigured
from .exceptions import MissingKey
from .exceptions import ResourceAlreadyExists
from .exceptions import ResourceDoesNotExist
from .exceptions import ResourceNotCreated
from .exceptions import ResourceNotDeleted
from .exceptions import WaitTimedOut

from . import clusters as cluster_jobs
from . import taskdefinitions as taskdef_jobs

from . import utils


def get_display_name(record):
    """Get the display name for a record.

    Args:

        record
            A record returned by AWS.

    Returns:
        A display name for the task.

    """
    name = record.get("startedBy")
    if not name:
        name = "Unnamed"
    return str(name) + " (" + str(record["taskArn"]) + ")"


def fetch_all(profile, cluster):
    """Fetch all tasks in a cluster.

    Args:

        profile
            A profile to connect to AWS with.

        cluster
            The name of a cluster.

    Returns:
        A list of tasks.

    """
    # Make sure the cluster exists.
    if not cluster_jobs.exists(profile, cluster):
        msg = "No cluster '" + str(cluster) + "'."
        raise ResourceDoesNotExist(msg)

    # Get all task ARNs in the cluster.
    params = {}
    params["profile"] = profile
    params["cluster"] = cluster
    response = utils.do_request(task, "get_arns", params)
    task_arns = utils.get_data("taskArns", response)

    # Now fetch their details.
    data = None
    if task_arns:
        params = {}
        params["profile"] = profile
        params["cluster"] = cluster
        params["tasks"] = task_arns
        response = utils.do_request(task, "get", params)
        data = utils.get_data("tasks", response)

    return data


def fetch_by_name(profile, cluster, name):
    """Fetch tasks in a cluster by name.

    Args:

        profile
            A profile to connect to AWS with.

        cluster
            The name of a cluster.

        name
            The name of the task you want to get.

    Returns:
        A list of matching tasks.

    """
    # Make sure the cluster exists.
    if not cluster_jobs.exists(profile, cluster):
        msg = "No cluster '" + str(cluster) + "'."
        raise ResourceDoesNotExist(msg)

    # Get all task ARNs in the cluster with the specified name.
    params = {}
    params["profile"] = profile
    params["cluster"] = cluster
    params["started_by"] = name
    response = utils.do_request(task, "get_arns", params)
    task_arns = utils.get_data("taskArns", response)

    # Now fetch their details.
    data = None
    if task_arns:
        params = {}
        params["profile"] = profile
        params["cluster"] = cluster
        params["tasks"] = task_arns
        response = utils.do_request(task, "get", params)
        data = utils.get_data("tasks", response)

    return data


def exists(profile, name):
    """Check if a task exists.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The full FAMILY:REVISION name of a task definition.

    Returns:
        True if it exists, False if it doesn't.

    """
    result = fetch_by_name(profile, name)
    return True if result else False


def create(profile, name, cluster, task_definition, count=None):
    """Run a task in a cluster.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name you want to give to the task.

        cluster
            The name of a cluster to run the task in.

        task_definition
            The task definition to run the task from.

        count
            The number of copies of the task to run.

    Returns:
        Info about the task.

    """
    # Make sure the cluster exists.
    if not cluster_jobs.exists(profile, cluster):
        msg = "No cluster '" + str(cluster) + "'."
        raise ResourceDoesNotExist(msg)

    # Make sure the task definition exists.
    if not taskdef_jobs.exists(profile, task_definition):
        msg = "No task definition '" + str(task_definition) + "'."
        raise ResourceDoesNotExist(msg)
    
    # Start the task.
    params = {}
    params["profile"] = profile
    params["cluster"] = cluster
    params["task_definition"] = task_definition
    params["started_by"] = name
    params["count"] = count
    response = utils.do_request(task, "create", params)

    # Check for failures.
    failures = utils.get_data("failures", response)
    if failures:
        reason = failures[0]["reason"]
        msg = "Task didn't start. " + str(reason) + "."
        raise ResourceNotCreated(msg)

    # Get the task's info.
    data = utils.get_data("tasks", response)
    return data


def delete(profile, cluster, name):
    """Delete a task in a cluster.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name of the task to delete.

    """
    # Make sure it exists.
    task_data = fetch_by_name(profile, cluster, name)
    if not task_data:
        msg = "No task '" + str(name) + "'."
        raise ResourceDoesNotExist(msg)

    # Delete each one.
    task_arns = [x["taskArn"] for x in task_data]
    for task_arn in task_arns:
        params = {}
        params["profile"] = profile
        params["cluster"] = cluster
        params["task_id"] = task_arn
        response = utils.do_request(task, "delete", params)

    # Make sure that they were, in fact, deleted.
    task_data = fetch_by_name(profile, cluster, name)
    if task_data:
        msg = "Task '" + str(name) + "' not deleted."
        raise ResourceNotDeleted(msg)
