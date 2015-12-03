# -*- coding: utf-8 -*-

"""Utilities for working with EC2 instances."""

from . import client as boto3client


def wait_for_instances_to_terminate(profile, instances):
    """Block/wait until the provided EC2 instances terminate.

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
