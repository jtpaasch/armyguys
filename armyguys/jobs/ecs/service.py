# -*- coding: utf-8 -*-

"""For creating and managing ECS tasks."""

from botocore.exceptions import ClientError

from ...aws import ecs
from ...aws import profile

from ...jobs import utils


def get_service_info(aws_profile, cluster, service_name):
    """Get info about a service.

    Args:

        aws_profile
            A profile to connect to AWS with.

        cluster
            The name of the cluster the service is running in.

        service_name
            The name of the service.

    Returns:
        The JSON response returned by boto3 regarding the service.

    """
    params = {}
    params["profile"] = aws_profile
    params["cluster"] = cluster
    params["service"] = service_name
    response = ecs.service.get(**params)
    services = response["services"]
    service = None
    if services:
        service = response["services"][0]
    return service


def get_task_definition_info(aws_profile, task_definition):
    """Get info about a task definition.

    Args:

        aws_profile
            A profile to connect to AWS with.

        task_definition
            The task definition you want info about, in the
            form <family:revision>.

    Returns:
        The JSON response returned by boto3 regarding the task definition.

    """
    result = None
    params = {}
    params["profile"] = aws_profile
    params["task_definition"] = task_definition
    try:
        response = ecs.taskdefinition.get(**params)
    except ClientError as e:
        bad_message = "Unable to describe task definition"
        if e.response["Error"]["Message"].startswith(bad_message):
            response = None
    if response:
        result = response[0]
    return result


def clean_service_response(response):
    """Remove the 'events' list from a service response.

    Args:

        response
            Data returned by boto3 about a service.
            It should contain a service->events field.

    Returns:
        The same response, but without the service->events field.

    """
    service_data = response.get("service")
    if service_data:
        events_data = service_data.get("events")
        if events_data:
            del response["service"]["events"]
    return response


def start_service(
        aws_profile,
        cluster,
        service_name,
        task_definition,
        count=1):
    """Start a service in an ECS cluster.

    Args:

        aws_profile
            A profile to connect to AWS with.

        cluster
            The name of the cluster you want to run the service in.

        service_name
            The name of the service you want to stop.

        task_definition
            The task definition to run as a service (in the form
            of <family:revision>).

        count
            The number of copies of the service you want to run
            simultaneously.

    """
    # Make sure there isn't an already active service by the same name.
    utils.heading("Checking that the service isn't already active")
    service_info = get_service_info(aws_profile, cluster, service_name)
    status = service_info.get("status")
    if status == "ACTIVE":
        utils.error("Service is already active")
        utils.exit()
    elif status == "DRAINING":
        utils.error("Service is draining. Try again later.")
        utils.exit()
    else:
        utils.echo("OK. No service '" + service_name + "' is active.")

    # Make sure the task definition exists.
    utils.heading("Checking that the task definition exists")
    task_definition_info = get_task_definition_info(aws_profile, task_definition)
    if not task_definition_info:
        utils.error("No such task definition '" + task_definition + "'.")
        utils.exit()
    else:
        utils.echo("OK. Found task definition '" + task_definition + "'.")

    # Start the service.
    utils.heading("Starting service")
    params = {}
    params["profile"] = aws_profile
    params["cluster"] = cluster
    params["task_definition"] = task_definition
    params["name"] = service_name
    params["count"] = count
    response = ecs.service.create(**params)
    response = clean_service_response(response)
    utils.echo_data(response)

    # Exit nicely.
    utils.echo("Done.")


def stop_service(
        aws_profile,
        cluster,
        service_name):
    """Stop a service in an ECS cluster.

    Args:

        aws_profile
            A profile to connect to AWS with.

        cluster
            The name of the cluster you want to stop the service in.

        service_name
            The name of the service you want to stop.

    """
    # Make sure there is a service to shut down.
    utils.heading("Checking that the service isn't already deactivated")
    service_info = get_service_info(aws_profile, cluster, service_name)
    status = service_info.get("status")
    if status == "INACTIVE":
        utils.error("Service is already inactive.")
        utils.exit()
    elif status == "DRAINING":
        utils.error("Service is already draining.")
        utils.exit()
    else:
        utils.echo("OK. Service '" + service_name + "' is active.")

    # Scale down the number of containers to 0.
    utils.heading("Scaling down service")
    response = ecs.service.update(
        profile=aws_profile,
        cluster=cluster,
        service=service_name,
        count=0)
    response = clean_service_response(response)
    utils.echo_data(response)
        
    # Stop the service.
    utils.heading("Stopping service")
    response = ecs.service.delete(
        profile=aws_profile,
        cluster=cluster,
        service=service_name)
    response = clean_service_response(response)
    utils.echo_data(response)


if __name__ == "__main__":
    # Examples:
    
    # Get an AWS profile.
    aws_profile = profile.configured()

    # Define some parameters.
    cluster = "joe-cluster"
    task_definition = "simpleton:6"
    service_name = "simpleton"
    count = 1

    # Stop the service.
    # stop_service(aws_profile, cluster, service_name)
    # utils.exit()

    # Or, start the service.
    start_service(
        aws_profile=aws_profile,
        cluster=cluster,
        task_definition=task_definition,
        service_name=service_name,
        count=count)
