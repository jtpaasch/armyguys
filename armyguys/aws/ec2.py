# -*- coding: utf-8 -*-

"""Utilities for working with EC2 instances."""

from time import sleep

from botocore.exceptions import ClientError

from . import client as boto3client


def wait_for_instances_to_terminate_2(profile, instances):
    """Block/wait until the provided EC2 instances terminate.

    Note:
        This will only wait on EC2 instances that are actively being
        terminated. If the instances are, say, in a pending state,
        this will throw an exception.

    Args:

        profile
            A profile to connect to AWS with.

        instances
            A list of EC2 instance IDs to watch until they terminate.

    Returns:
        This function returns nothing. Instead, it just blocks
        the process and doesn't return control until the
        instances are terminated.

    """
    client = boto3client.get("ec2", profile)
    waiter = client.get_waiter("instance_terminated")
    waiter.config.max_attempts = 15
    waiter.wait(InstanceIds=instances)


def stop(profile, instances):
    """Stop EC2 instances.

    Args:

        profile
            A profile to connect to AWS with.

        instances
            A list of EC2 instance IDs to stop.

    Returns:
        The JSON returned by boto3.

    """
    client = boto3client.get("ec2", profile)
    params = {}
    params["InstanceIds"] = instances
    return client.stop_instances(**params)


def wait_until_gone(profile, instance, max_attempts=5, wait_interval=1):
    """Block/wait until the provided EC2 instance is terminated.

    This is more resilient than the ``wait_for_instances_to_terminate()``
    function above; this one can handle EC2 instances in any state.

    Args:

        profile
            A profile to connect to AWS with.

        instance
            The ID of an EC2 instance you want to watch until it's terminated.

        max_attempts
            The number of times you want to poll AWS to check on the instance.

        wait_interval
            The number of seconds to wait between each poll.

    Returns:
        A boolean indiicating success.

    """
    client = boto3client.get("ec2", profile)
    params = {}
    params["InstanceIds"] = [instance]
    count = 0
    is_gone = False
    while True:
        if count >= max_attempts:
            break
        else:

            try:
                response = client.describe_instances(**params)
            except ClientError as error:
                error_code = error.response["Error"]["Code"]
                if error_code == "InvalidInstanceID.NotFound":
                    is_gone = True
                    break
                else:
                    raise
            instance = response["Reservations"][0]["Instances"][0]
            status = instance["State"]["Name"]
            if status == "terminated":
                is_gone = True
                break
        count += 1
        sleep(wait_interval)
    return is_gone
