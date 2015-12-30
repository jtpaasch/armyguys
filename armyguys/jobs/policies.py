# -*- coding: utf-8 -*-

"""Jobs for IAM policies."""

import os

from ..aws.iam import policy

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
        A display name for the policy.

    """
    return record["PolicyName"]


def fetch_all(profile):
    """Fetch all policies.

    Args:

        profile
            A profile to connect to AWS with.

    Returns:
        A list of policies.

    """
    params = {}
    params["profile"] = profile
    response = utils.do_request(policy, "get", params)
    data = utils.get_data("Policies", response)
    return data


def fetch_by_name(profile, name):
    """Fetch a policy by name.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name of the policy you want to fetch.

    Returns:
        A list of policies with the provided name.

    """
    params = {}
    params["profile"] = profile
    response = utils.do_request(policy, "get", params)
    data = utils.get_data("Policies", response)
    result = [x for x in data if x["PolicyName"] == name]
    return result


def exists(profile, name):
    """Check if a policy exists.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name of a policy.

    Returns:
        True if it exists, False if it doesn't.

    """
    result = fetch_by_name(profile, name)
    return len(result) > 0


def polling_fetch(profile, name, max_attempts=10, wait_interval=1):
    """Try to fetch a policy repeatedly until it exists.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name of a policy.

        max_attempts
            The max number of times to poll AWS.

        wait_interval
            How many seconds to wait between each poll.

    Returns:
        The policy's data, or None if it times out.

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
        msg = "Timed out waiting for policy to be created."
        raise WaitTimedOut(msg)
    return data


def create(profile, name, filepath=None, contents=None):
    """Create a policy.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name you want to give to the policy.

        filepath
            The path to a file. If you provide this, leave
            the ``contents`` parameter blank.

        contents
            The contents of a file. If you provide this, leave
            the ``filepath`` parameter blank.

    Returns:
        Info about the newly created policy.

    """
    # Make sure only contents or a filepath are specified.
    if all([filepath, contents]) or not any([filepath, contents]):
        msg = "Provide either a file path or its contents, but not both."
        raise ImproperlyConfigured(msg)

    # Make sure the file exists, if a filepath was specified.
    if filepath:
        if not os.path.isfile(filepath):
            msg = "No such file '" + str(filepath) + "'."
            raise FileDoesNotExist(msg)

    # Make sure the policy doesn't exist already.
    if exists(profile, name):
        msg = "Policy '" + str(name) + "' already exists."
        raise ResourceAlreadyExists(msg)

    # Now we can create it.
    params = {}
    params["profile"] = profile
    params["name"] = name
    if filepath:
        params["filepath"] = filepath
    elif contents:
        params["contents"] = contents
    response = utils.do_request(policy, "create", params)

    # Check that it exists.
    policy_data = polling_fetch(profile, name)
    if not policy_data:
        msg = "Policy '" + str(name) + "' not created."
        raise ResourceNotCreated(msg)

    # Send back the policy's info.
    return policy_data


def delete(profile, name):
    """Delete an IAM policy.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name of the policy you want to delete.

    """
    # Make sure the policy exists.
    policy_data = fetch_by_name(profile, name)
    if not policy_data:
        msg = "No policy '" + str(name) + "'."
        raise ResourceDoesNotExist(msg)
    policy_arn = policy_data[0]["Arn"]

    # Now try to delete it.
    params = {}
    params["profile"] = profile
    params["policy"] = policy_arn
    response = utils.do_request(policy, "delete", params)

    # Check that it was, in fact, deleted.
    if exists(profile, name):
        msg = "The policy '" + str(name) + "' was not deleted."
        raise ResourceNotDeleted(msg)
