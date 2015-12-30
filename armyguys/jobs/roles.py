# -*- coding: utf-8 -*-

"""Jobs for IAM roles."""

import os

from ..aws.iam import role as role_lib

from .exceptions import FileDoesNotExist
from .exceptions import ImproperlyConfigured
from .exceptions import MissingKey
from .exceptions import ResourceAlreadyExists
from .exceptions import ResourceDoesNotExist
from .exceptions import ResourceNotCreated
from .exceptions import ResourceNotDeleted
from .exceptions import WaitTimedOut

from . import policies as policy_jobs

from . import utils


def get_display_name(record):
    """Get the display name for a record.

    Args:

        record
            A record returned by AWS.

    Returns:
        A display name for the role.

    """
    return record["RoleName"]


def fetch_all(profile):
    """Fetch all roles.

    Args:

        profile
            A profile to connect to AWS with.

    Returns:
        A list of roles.

    """
    params = {}
    params["profile"] = profile
    response = utils.do_request(role_lib, "get", params)
    data = utils.get_data("Roles", response)
    return data


def fetch_by_name(profile, name):
    """Fetch a role by name.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name of the role you want to fetch.

    Returns:
        A list of roles with the provided name.

    """
    params = {}
    params["profile"] = profile
    response = utils.do_request(role_lib, "get", params)
    data = utils.get_data("Roles", response)
    result = [x for x in data if x["RoleName"] == name]
    return result


def exists(profile, name):
    """Check if a role exists.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name of a role.

    Returns:
        True if it exists, False if it doesn't.

    """
    result = fetch_by_name(profile, name)
    return len(result) > 0


def create(profile, name, filepath=None, contents=None):
    """Create a role.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name you want to give to the role.

        filepath
            The path to a file. If you provide this, leave
            the ``contents`` parameter blank.

        contents
            The contents of a file. If you provide this, leave
            the ``filepath`` parameter blank.

    Returns:
        Info about the newly created role.

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

    # Make sure the role doesn't exist already.
    if exists(profile, name):
        msg = "Role '" + str(name) + "' already exists."
        raise ResourceAlreadyExists(msg)

    # Now we can create it.
    params = {}
    params["profile"] = profile
    params["name"] = name
    if filepath:
        params["filepath"] = filepath
    elif contents:
        params["contents"] = contents
    response = utils.do_request(role_lib, "create", params)

    # Check that it exists.
    role_data = fetch_by_name(profile, name)
    if not role_data:
        msg = "Role '" + str(name) + "' not created."
        raise ResourceNotCreated(msg)

    # Send back the role's info.
    return role_data


def delete(profile, name):
    """Delete an IAM role.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name of the role you want to delete.

    """
    # Make sure the role exists.
    if not exists(profile, name):
        msg = "No role '" + str(name) + "'."
        raise ResourceDoesNotExist(msg)

    # Now try to delete it.
    params = {}
    params["profile"] = profile
    params["role"] = name
    response = utils.do_request(role_lib, "delete", params)

    # Check that it was, in fact, deleted.
    if exists(profile, name):
        msg = "The role '" + str(name) + "' was not deleted."
        raise ResourceNotDeleted(msg)


def attach(profile, role, policy):
    """Attach an IAM policy to an IAM role.

    Args:

        profile
            A profile to connect to AWS with.

        role
            The name of a role.

        policy
            The name of a policy.

    Returns:
        The data returned by boto3.

    """
    # Make sure the role exists.
    if not exists(profile, role):
        msg = "No role '" + str(role) + "'."
        raise ResourceDoesNotExist(msg)

    # Make sure the policy exists.
    policy_data = policy_jobs.fetch_by_name(profile, policy)
    if not policy_data:
        msg = "No policy '" + str(policy) + "'."
        raise ResourceDoesNotExist(msg)

    # Get the policy's ARN.
    policy_arn = policy_data[0]["Arn"]
    
    # Attach the policy to the role.
    params = {}
    params["profile"] = profile
    params["role"] = role
    params["policy"] = policy_arn
    utils.do_request(role_lib, "attach_policy", params)


def detach(profile, role, policy):
    """Detach an IAM policy from an IAM role.

    Args:

        profile
            A profile to connect to AWS with.

        role
            The name of a role.

        policy
            The name of a policy.

    Returns:
        The data returned by boto3.

    """
    # Make sure the role exists.
    if not exists(profile, role):
        msg = "No role '" + str(role) + "'."
        raise ResourceDoesNotExist(msg)

    # Make sure the policy exists.
    policy_data = policy_jobs.fetch_by_name(profile, policy)
    if not policy_data:
        msg = "No policy '" + str(policy) + "'."
        raise ResourceDoesNotExist(msg)

    # Get the policy's ARN.
    policy_arn = policy_data[0]["Arn"]

    # Detach the policy.
    params = {}
    params["profile"] = profile
    params["role"] = role
    params["policy"] = policy_arn
    utils.do_request(role_lib, "detach_policy", params)
