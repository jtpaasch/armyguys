# -*- coding: utf-8 -*-

"""Jobs for ECS task definitions."""

import os

from ..aws.ecs import taskdefinition

from .exceptions import FileDoesNotExist
from .exceptions import ImproperlyConfigured
from .exceptions import MissingKey
from .exceptions import ResourceAlreadyExists
from .exceptions import ResourceDoesNotExist
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
        A display name for the task definition.

    """
    return str(record["family"]) + ":" + str(record["revision"])


def get_display_name_from_arn(record):
    """Get the display name for a version from its ARN.

    Args:

        record
            A record returned by AWS.

    Returns:
        A display name for the task definition version.

    """
    arn_parts = record.split(":")
    name = arn_parts[5]
    version = arn_parts[6]
    name_parts = name.split("/")
    family = name_parts[1]
    return str(family) + ":" + str(version)

def fetch_all(profile):
    """Fetch all task definition versions from all families.

    Args:

        profile
            A profile to connect to AWS with.

    Returns:
        A list of task definition versions.

    """
    params = {}
    params["profile"] = profile
    response = utils.do_request(taskdefinition, "get_arns", params)
    data = utils.get_data("taskDefinitionArns", response)
    return data


def fetch_families(profile):
    """Fetch all task definition families.

    Args:

        profile
            A profile to connect to AWS with.

    Returns:
        A list of task definitions.

    """
    params = {}
    params["profile"] = profile
    response = utils.do_request(taskdefinition, "get_families", params)
    data = utils.get_data("families", response)
    return data


def fetch_versions(profile, family):
    """Fetch all task definition versions for a family.

    Args:

        profile
            A profile to connect to AWS with.

        family
            An ECS task definition family.

    Returns:
        A list of task definition versions.

    """
    params = {}
    params["profile"] = profile
    params["family"] = family
    response = utils.do_request(taskdefinition, "get_arns", params)
    data = utils.get_data("taskDefinitionArns", response)
    return data


def fetch_error_handler(error):
    """Handle errors that arise when you try to fetch task definitions.

    Args:

        error
            An AWS ``ClientError`` exception.

    Raises:
        ``ResourceDoesNotExist`` if AWS can't describe the task definition.

    Returns:
        None, if the error is not worth handling.

    """
    message = error.response["Error"]["Message"]
    if message == "Unable to describe task definition.":
        msg = "No task definition."
        raise ResourceDoesNotExist(msg)


def fetch_by_name(profile, name):
    """Fetch a task definition by full FAMILY:VERSION name.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The full FAMILY:VERSION name of a task definition.

    Returns:
        The task definition's info.

    """
    params = {}
    params["profile"] = profile
    params["task_definition"] = name
    response = None
    try:
        response = utils.do_request(
            taskdefinition,
            "get",
            params,
            error_handler=fetch_error_handler)
    except ResourceDoesNotExist:
        pass
    data = None
    if response:
        data = utils.get_data("taskDefinition", response)
    if data:
        status = data["status"]
        if status != "ACTIVE":
            data = None
    return data


def exists(profile, name):
    """Check if a task definition exists.

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


def polling_fetch(profile, bucket, name, max_attempts=10, wait_interval=1):
    """Try to fetch a file in a bucket repeatedly until it exists.

    Args:

        profile
            A profile to connect to AWS with.

        bucket
            The name of the bucket you want to find the file in..

        name
            The name of the file you want to fetch.

        max_attempts
            The max number of times to poll AWS.

        wait_interval
            How many seconds to wait between each poll.

    Returns:
        The file's info, or None if it times out.

    """
    data = None
    count = 0
    while count < max_attempts:
        data = fetch_by_name(profile, bucket, name)
        if data:
            break
        else:
            count += 1
            sleep(wait_interval)
    if not data:
        msg = "Timed out waiting for file to be created."
        raise WaitTimedOut(msg)
    return data


def create(profile, filepath=None, contents=None):
    """Create a task definition.

    Args:

        profile
            A profile to connect to AWS with.

        filepath
            The path to a file. If you provide this, leave
            the ``filepath`` parameter blank.

        contents
            The contents of a file. If you provide this, leave
            the ``contents`` parameter blank.

    Returns:
        Info about the newly created task definition.

    """
    params = {}
    params["profile"] = profile
    if filepath:
        params["filepath"] = filepath
    elif contents:
        params["contents"] = contents
    response = utils.do_request(taskdefinition, "create", params)
    data = utils.get_data("taskDefinition", response)
    return data



def delete(profile, name):
    """Delete an ECS task definition.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The full FAMILY:VERSION name of a task definition.

    """
    # Check that it doesn't exist already.
    if not exists(profile, name):
        msg = "No task definition '" + str(name) + "'."
        raise ResourceAlreadyExists(msg)

    # Try to delete it.
    params = {}
    params["profile"] = profile
    params["name"] = name
    response = utils.do_request(taskdefinition, "delete", params)

    # Check that it was, in fact, deleted.
    if exists(profile, name):
        msg = "The task definition '" + str(name) + "' was not deleted."
        raise ResourceNotDeleted(msg)
