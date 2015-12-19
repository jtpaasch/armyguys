# -*- coding: utf-8 -*-

"""Jobs for auto scaling groups."""

from time import sleep

from botocore.exceptions import ClientError

from ..aws.autoscaling import autoscalinggroup

from . import launchconfigs as launchconfig_jobs

from .exceptions import ResourceAlreadyExists
from .exceptions import ResourceDoesNotExist
from .exceptions import ResourceHasDependency
from .exceptions import ResourceNotCreated
from .exceptions import ResourceNotDeleted
from .exceptions import WaitTimedOut

from . import utils


def get_display_name(record):
    """Get the display name for a record.

    Args:

        record
            A record returned by AWS.

    Returns:
        A display name for the auto scaling group.

    """
    return record["AutoScalingGroupName"]


def fetch_all(profile):
    """Fetch all auto scaling groups.

    Args:

        profile
            A profile to connect to AWS with.

    Returns:
        A list of auto scaling groups.

    """
    params = {}
    params["profile"] = profile
    response = utils.do_request(autoscalinggroup, "get", params)
    data = utils.get_data("AutoScalingGroups", response)
    return data


def fetch_by_name(profile, name):
    """Fetch auto scaling groups by name.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name of the auto scaling group you want to fetch.

    Returns:
        A list of matching auto scaling groups.

    """
    params = {}
    params["profile"] = profile
    params["autoscaling_group"] = name
    response = utils.do_request(autoscalinggroup, "get", params)
    data = utils.get_data("AutoScalingGroups", response)
    return data


def is_auto_scaling_group(profile, name):
    """Check if an auto scaling group exists.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name of an auto scaling group.

    Returns:
        True if it exists, False if it doesn't.

    """
    result = fetch_by_name(profile, name)
    return len(result) > 0


def polling_fetch(profile, name, max_attempts=10, wait_interval=1):
    """Try to fetch an auto scaling group repeatedly until it exists.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name of an auto scaling group.

        max_attempts
            The max number of times to poll AWS.

        wait_interval
            How many seconds to wait between each poll.

    Returns:
        The auto scaling group's info, or None if it times out.

    """
    data = None
    count = 0
    while count < max_attempts:
        data = fetch_by_name(profile, name)
        if data:
            break
        else:
            count += 1
            sleep(wait_interval)
    if not data:
        msg = "Timed out waiting for auto scaling group to be created."
        raise WaitTimedOut(msg)
    return data


def create(
        profile,
        name,
        launch_configuration):
    """Create an auto scaling group.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name you want to give to a security group.

        launch_configuration
            The name of a launch configuration to launch from.

    Returns:
        The auto scaling group's info.

    """
    # Check that the launch configuration exists.
    if not launchconfig_jobs.fetch_by_name(profile, launch_configuration):
        msg = "No launch configuration '" + str(launch_configuration) + "'."
        raise ResourceDoesNotExist(msg)

    # Now we can create it.
    params = {}
    params["profile"] = profile
    params["name"] = name
    params["launch_configuration"] = launch_configuration
    response = utils.do_request(autoscalinggroup, "create", params)

    # Now check that it exists.
    auto_scaling_group_data = None
    try:
        auto_scaling_group_data = polling_fetch(profile, name)
    except WaitTimedOut:
        msg = "Timed out waiting for '" + str(name) + "' to be created."
        raise ResourceNotCreated(msg)
    if not auto_scaling_group_data:
        msg = "Auto scaling group '" + str(name) + "' not created."
        raise ResourceNotCreated(msg)

    # Send back the auto scaling group's info.
    return auto_scaling_group_data


def delete(profile, name):
    """Delete a launch configuration.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name of the launch configuration you want to delete.

    """
    # Make sure it exists before we try to delete it.
    launch_config = fetch_by_name(profile, name)
    if not launch_config:
        msg = "No launch configuration '" + str(name) + "'."
        raise ResourceDoesNotExist(msg)

    # Now try to delete it.
    params = {}
    params["profile"] = profile
    params["launch_configuration"] = name
    response = utils.do_request(launchconfiguration, "delete", params)

    # Check that it was, in fact, deleted.
    launch_config = fetch_by_name(profile, name)
    if launch_config:
        msg = "Launch configuration '" + str(name) + "' was not deleted."
        raise ResourceNotDeleted(msg)
