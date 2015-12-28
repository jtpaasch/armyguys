# -*- coding: utf-8 -*-

"""Jobs for ECS services."""

import os

from ..aws.ecs import service

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
        A display name for the service.

    """
    return str(record["serviceName"]) + " (" + str(record["serviceArn"]) + ")"


def fetch_all(profile, cluster):
    """Fetch all services in a cluster.

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

    # Get all service ARNs in the cluster.
    params = {}
    params["profile"] = profile
    params["cluster"] = cluster
    response = utils.do_request(service, "get_arns", params)
    service_arns = utils.get_data("serviceArns", response)

    # Now fetch their details.
    data = None
    if service_arns:
        params = {}
        params["profile"] = profile
        params["cluster"] = cluster
        params["services"] = service_arns
        response = utils.do_request(service, "get", params)
        data = utils.get_data("services", response)

    return data


def fetch_by_name(profile, cluster, name):
    """Fetch services in a cluster by name.

    Args:

        profile
            A profile to connect to AWS with.

        cluster
            The name of a cluster.

        name
            The name of the service you want to get.

    Returns:
        A list of matching services.

    """
    # Make sure the cluster exists.
    if not cluster_jobs.exists(profile, cluster):
        msg = "No cluster '" + str(cluster) + "'."
        raise ResourceDoesNotExist(msg)

    # Find the matching service.
    params = {}
    params["profile"] = profile
    params["cluster"] = cluster
    params["services"] = [name]  # service_arns
    response = utils.do_request(service, "get", params)
    data = utils.get_data("services", response)
    return [x for x in data if x["status"] == "ACTIVE"]


def exists(profile, name):
    """Check if a service exists.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name of a service.

    Returns:
        True if it exists, False if it doesn't.

    """
    result = fetch_by_name(profile, name)
    return True if result else False


def create(profile, name, cluster, task_definition, count=None):
    """Start a service in a cluster.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name you want to give to the service.

        cluster
            The name of a cluster to run the service in.

        task_definition
            The task definition to run the service from.

        count
            The number of copies of the service to run.

    Returns:
        Info about the service.

    """
    # Make sure the cluster exists.
    if not cluster_jobs.exists(profile, cluster):
        msg = "No cluster '" + str(cluster) + "'."
        raise ResourceDoesNotExist(msg)

    # Make sure the task definition exists.
    if not taskdef_jobs.exists(profile, task_definition):
        msg = "No task definition '" + str(task_definition) + "'."
        raise ResourceDoesNotExist(msg)
    
    # Start the service.
    params = {}
    params["profile"] = profile
    params["name"] = name
    params["cluster"] = cluster
    params["task_definition"] = task_definition
    if count:
        params["count"] = count
    response = utils.do_request(service, "create", params)

    # Check for failures.
    failures = None
    try:
        failures = utils.get_data("failures", response)
    except MissingKey:
        pass
    if failures:
        reason = failures[0]["reason"]
        msg = "Service didn't start. " + str(reason) + "."
        raise ResourceNotCreated(msg)

    # Get the service's info.
    data = utils.get_data("service", response)
    return data


def update(profile, name, cluster, task_definition=None, count=None):
    """Update a service in a cluster.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name of the service you want to update.

        cluster
            The name of a cluster teh service is running in.

        task_definition
            The full FAMILY:REVISION name of the task definition to run. 

        count
            The number of copies of the service to run.

    Returns:
        Info about the service.

    """
    # Make sure the cluster exists.
    if not cluster_jobs.exists(profile, cluster):
        msg = "No cluster '" + str(cluster) + "'."
        raise ResourceDoesNotExist(msg)

    # Make sure the task definition exists.
    if task_definition:
        if not taskdef_jobs.exists(profile, task_definition):
            msg = "No task definition '" + str(task_definition) + "'."
            raise ResourceDoesNotExist(msg)
    
    # Update the service.
    params = {}
    params["profile"] = profile
    params["service"] = name
    params["cluster"] = cluster
    if task_definition:
        params["task_definition"] = task_definition
    if count:
        params["count"] = count
    response = utils.do_request(service, "update", params)

    # Get the service's info.
    data = utils.get_data("service", response)
    return data


def polling_is_deleted(profile, cluster, name, max_attempts=10, wait_interval=1):
    """Try to fetch a service repeatedly, until it is deleted.

    Args:

        profile
            A profile to connect to AWS with.

        cluster
            The name of a cluster.

        name
            The name of the service you want to check.

        max_attempts
            The max number of times to poll AWS.

        wait_interval
            How many seconds to wait between each poll.

    Returns:
        The service's info, or None if it times out.

    """
    data = None
    count = 0
    while count < max_attempts:
        data = fetch_by_name(profile, cluster, name)
        if not data:
            break
        else:
            count += 1
            sleep(wait_interval)
    if data:
        msg = "Timed out waiting for service to be deleted."
        raise WaitTimedOut(msg)
    return data
        

def delete(profile, cluster, name):
    """Delete an ECS task definition.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name of the service you want to delete.

    """
    # Make sure it exists.
    service_data = fetch_by_name(profile, cluster, name)
    if not service_data:
        msg = "No service '" + str(name) + "'."
        raise ResourceDoesNotExist(msg)

    # Go through each service:
    service_arns = [x["serviceArn"] for x in service_data]
    for service_arn in service_arns:

        # Scale the service down to 0 running instances.
        params = {}
        params["profile"] = profile
        params["cluster"] = cluster
        params["service"] = service_arn
        params["count"] = 0
        response = utils.do_request(service, "update", params)

        # Now delete the service.
        params = {}
        params["profile"] = profile
        params["cluster"] = cluster
        params["service"] = service_arn
        response = utils.do_request(service, "delete", params)
        polling_is_deleted(profile, cluster, name)

    # Make sure that they were, in fact, deleted.
    service_data = fetch_by_name(profile, cluster, name)
    if service_data:
        msg = "Service '" + str(name) + "' not deleted."
        raise ResourceNotDeleted(msg)
