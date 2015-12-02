# -*- coding: utf-8 -*-

"""For creating and managing ECS tasks."""

from os import path
from pprint import pprint

from botocore.exceptions import ClientError

from polarexpress.aws.ecs import task
from polarexpress.aws.ecs import taskdefinition
from polarexpress.aws import profile

from polarexpress.tasks import utils


def get_task_definition_info(aws_profile, task_definition):
    """Get info about a task definition.

    Args:

        aws_profile
            A profile to connect to AWS with.

        task_definition
            The task definition in the form <family:revision>.

    Returns:
        The data returned by boto3.

    """
    result = None
    response = None
    try:
        response = taskdefinition.get(
            profile=aws_profile,
            task_definition=task_definition)
    except ClientError as error:
        error_message = error.response["Error"]["Message"]
        if not error_message.startswith("Unable to describe task definition"):
            raise
    if response:
        result = response[0]["taskDefinition"]
    return result


def is_task_running(aws_profile, cluster, task_definition_arn):
    """Check if a task is running in a cluster.

    Args:

        aws_profile
            A profile to connect to AWS with.

        cluster
            The cluster the task is running in.

        task_definition_arn
            The Amazon ARN of the task definition.

    Returns:
        The data returned by boto3.

    """
    result = False
    response = task.get(profile=aws_profile, cluster=cluster)
    if response:
        tasks = response["tasks"]
        for record in tasks:
            td_arn = record["taskDefinitionArn"]
            status = record["lastStatus"]
            if td_arn == task_definition_arn and status == "RUNNING":
                result = True
                break
    return result


def run_task(
        aws_profile,
        cluster,
        task_definition):
    """Run a task in an ECS cluster.

    Args:

        aws_profile
            A profile to connect to AWS with.

        cluster
            The name of a cluster to run the task in.

        task_definition
            The task definition in the form <family:revision>.

    """
    # Make sure the task definition is legit.
    utils.heading("Getting task definition info")
    td_info = get_task_definition_info(
        aws_profile,
        task_definition)
    if td_info:
        td_arn = td_info["taskDefinitionArn"]
        utils.echo_data(td_info)
    else:
        utils.error("No such task definition '" + task_definition + "'.")
        utils.exit()

    # Check if the task is running.
    utils.heading("Checking if task is already running")
    if is_task_running(aws_profile, cluster, td_arn):
        utils.error("Task is already running.")
        utils.exit()
    else:
        utils.emphasize("OK. Task is not running.")

    # Start the task.
    utils.heading("Running task")
    params = {}
    params["profile"] = aws_profile
    params["cluster"] = cluster
    params["task_definition"] = task_definition
    response = task.create(**params)
    utils.echo_data(response)
    tasks = response["tasks"]
    if tasks:
        task_arn = tasks[0]["taskArn"]
        utils.emphasize("TASK ARN: " + str(task_arn))
    else:
        utils.error("No tasks were started.")
        utils.exit()

    # Exit nicely.
    utils.echo("")
    utils.echo("Done.")


def stop_task(
        aws_profile,
        cluster,
        task_definition):
    """Stop a task in an ECS cluster.

    Args:

        aws_profile
            A profile to connect to AWS with.

        cluster
            The name of the cluster the task is running in.

        task_definition
            The task definition in the form <family:revision>.

    """
    pass
    # Check task definition.
    # Check if the task is running.
    # Stop the task.

if __name__ == "__main__":
    # Get an AWS profile.
    aws_profile = profile.configured()

    # Define some parameters.
    cluster="joe-cluster"
    task_definition="simpleton:6"

    # Run the task.
    run_task(
        aws_profile=aws_profile,
        cluster=cluster,
        task_definition=task_definition)

