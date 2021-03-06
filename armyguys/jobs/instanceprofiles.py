# -*- coding: utf-8 -*-

"""Jobs for IAM roles."""

import os

from ..aws.iam import instanceprofile

from .exceptions import FileDoesNotExist
from .exceptions import ImproperlyConfigured
from .exceptions import MissingKey
from .exceptions import ResourceAlreadyExists
from .exceptions import ResourceDoesNotExist
from .exceptions import ResourceNotCreated
from .exceptions import ResourceNotDeleted
from .exceptions import WaitTimedOut

from . import roles as role_jobs

from . import utils


def get_display_name(record):
    """Get the display name for a record.

    Args:

        record
            A record returned by AWS.

    Returns:
        A display name for the instance profile.

    """
    return record["InstanceProfileName"]


def fetch_all(profile):
    """Fetch all instance profiles.

    Args:

        profile
            A profile to connect to AWS with.

    Returns:
        A list of instance profiles.

    """
    params = {}
    params["profile"] = profile
    response = utils.do_request(instanceprofile, "get", params)
    data = utils.get_data("InstanceProfiles", response)
    return data


def fetch_by_name(profile, name):
    """Fetch an instance profile by name.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name of the instance profile you want to fetch.

    Returns:
        A list of instance profiles with the provided name.

    """
    params = {}
    params["profile"] = profile
    response = utils.do_request(instanceprofile, "get", params)
    data = utils.get_data("InstanceProfiles", response)
    result = [x for x in data if x["InstanceProfileName"] == name]
    return result


def exists(profile, name):
    """Check if an instance profile exists.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name of an instance profile.

    Returns:
        True if it exists, False if it doesn't.

    """
    result = fetch_by_name(profile, name)
    return len(result) > 0


def polling_fetch(profile, name, max_attempts=10, wait_interval=1):
    """Try to fetch an instance profile repeatedly until it exists.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name of an instance profile.

        max_attempts
            The max number of times to poll AWS.

        wait_interval
            How many seconds to wait between each poll.

    Returns:
        The instance profile's data, or None if it times out.

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
        msg = "Timed out waiting for instance profile to be created."
        raise WaitTimedOut(msg)
    return data


def create(profile, name):
    """Create an instance profile.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name you want to give to the instance profile.

    Returns:
        Info about the newly created instance profile.

    """
    # Make sure it doesn't exist already.
    if exists(profile, name):
        msg = "Instance profile '" + str(name) + "' already exists."
        raise ResourceAlreadyExists(msg)

    # Now we can create it.
    params = {}
    params["profile"] = profile
    params["name"] = name
    response = utils.do_request(instanceprofile, "create", params)

    # Check that it exists.
    instance_profile_data = polling_fetch(profile, name)
    if not instance_profile_data:
        msg = "Instance profile '" + str(name) + "' not created."
        raise ResourceNotCreated(msg)

    # Send back the instance profile's info.
    return instance_profile_data


def delete(profile, name):
    """Delete an IAM instance profile.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name of the instance profile you want to delete.

    """
    # Make sure the instance profile exists.
    if not exists(profile, name):
        msg = "No instance profile '" + str(name) + "'."
        raise ResourceDoesNotExist(msg)

    # Now try to delete it.
    params = {}
    params["profile"] = profile
    params["name"] = name
    response = utils.do_request(instanceprofile, "delete", params)

    # Check that it was, in fact, deleted.
    if exists(profile, name):
        msg = "The instance profile '" + str(name) + "' was not deleted."
        raise ResourceNotDeleted(msg)


def attach(profile, instance_profile, role):
    """Attach an IAM role to an instance profile.

    Args:

        profile
            A profile to connect to AWS with.

        instance_profile
            The name of an instance profile.

        role
            The name of a role.

    Returns:
        The data returned by boto3.

    """
    # Make sure the instance profile exists.
    if not exists(profile, instance_profile):
        msg = "No instance profile '" + str(instance_profile) + "'."
        raise ResourceDoesNotExist(msg)

    # Make sure the role exists.
    if not role_jobs.exists(profile, role):
        msg = "No role '" + str(role) + "'."
        raise ResourceDoesNotExist(msg)
    
    # Attach the role to the instance profile.
    params = {}
    params["profile"] = profile
    params["instance_profile"] = instance_profile
    params["role"] = role
    return utils.do_request(instanceprofile, "add_role", params)


def detach(profile, instance_profile, role):
    """Detach an IAM role from an instance profile.

    Args:

        profile
            A profile to connect to AWS with.

        instance profile
            The name of an instance profile.

        role
            The name of a role.

    Returns:
        The data returned by boto3.

    """
    # Make sure the instance profile exists.
    if not exists(profile, instance_profile):
        msg = "No instance profile '" + str(instance_profile) + "'."
        raise ResourceDoesNotExist(msg)

    # Make sure the role exists.
    if not role_jobs.exists(profile, role):
        msg = "No role '" + str(role) + "'."
        raise ResourceDoesNotExist(msg)

    # Detach the role
    params = {}
    params["profile"] = profile
    params["instance_profile"] = instance_profile
    params["role"] = role
    return utils.do_request(instanceprofile, "remove_role", params)


def is_attached(profile, instance_profile, role):
    """Check if an IAM role is attached to an instance profile.

    Args:

        profile
            A profile to connect to AWS with.

        instance_profile
            The name of an instance profile.

        role
            The name of a role.

    Returns:
        True if it's attached, False if it's not.

    """
    # Make sure the instance profile exists.
    instance_profile_data = fetch_by_name(profile, instance_profile)
    if not instance_profile_data:
        msg = "No instance profile '" + str(instance_profile) + "'."
        raise ResourceDoesNotExist(msg)

    # Make sure the role exists.
    if not role_jobs.exists(profile, role):
        msg = "No role '" + str(role) + "'."
        raise ResourceDoesNotExist(msg)

    # Check if the role is attached.
    roles = utils.get_data("Roles", instance_profile_data[0])
    matching_roles = [x for x in roles if x["RoleName"] == role]
    return len(matching_roles) > 0


def is_detached(profile, instance_profile, role):
    """Check if an IAM role is detached from an instance profile.

    Args:

        profile
            A profile to connect to AWS with.

        instance_profile
            The name of an instance profile.

        role
            The name of a role.

    Returns:
        True if it's detached, False if it's not.

    """
    # Make sure the instance profile exists.
    instance_profile_data = fetch_by_name(profile, instance_profile)
    if not instance_profile_data:
        msg = "No instance profile '" + str(instance_profile) + "'."
        raise ResourceDoesNotExist(msg)

    # Make sure the role exists.
    if not role_jobs.exists(profile, role):
        msg = "No role '" + str(role) + "'."
        raise ResourceDoesNotExist(msg)

    # Check if the role is detached.
    roles = utils.get_data("Roles", instance_profile_data[0])
    matching_roles = [x for x in roles if x["RoleName"] == role]
    return len(matching_roles) == 0
