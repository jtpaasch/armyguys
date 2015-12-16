# -*- coding: utf-8 -*-

"""Jobs for security groups."""

from time import sleep

from botocore.exceptions import ClientError

from ..aws import securitygroup

from .exceptions import ResourceAlreadyExists
from .exceptions import ResourceDoesNotExist
from .exceptions import ResourceHasDependency
from .exceptions import ResourceNotCreated
from .exceptions import ResourceNotDeleted
from .exceptions import WaitTimedOut

from . import utils

from . import vpcs as vpc_jobs


def get_display_name(record):
    """Get the display name for a record.

    Args:

        record
            A record returned by AWS.

    Returns:
        A display name for the security group.

    """
    return str(record["GroupName"]) + " (" + str(record["GroupId"]) + ")"


def get_id(record):
    """Get the ID from a record.

    Args:

        record
            A record returned by AWS.

    Returns:
        The ID for the record.

    """
    return str(record["GroupId"])


def fetch_all(profile):
    """Fetch all security groups.

    Args:

        profile
            A profile to connect to AWS with.

    Returns:
        A list of security groups.

    """
    params = {}
    params["profile"] = profile
    response = utils.do_request(securitygroup, "get", params)
    data = utils.get_data("SecurityGroups", response)
    return data


def fetch_by_id(profile, ref):
    """Fetch security groups by ID.

    Args:

        profile
            A profile to connect to AWS with.

        ref
            The ID of the security group you want to fetch.

    Returns:
        A list of matching security groups.

    """
    params = {}
    params["profile"] = profile
    params["filters"] = [{"Name": "group-id", "Values": [ref]}]
    response = utils.do_request(securitygroup, "get", params)
    data = utils.get_data("SecurityGroups", response)
    return data


def fetch_by_name(profile, name):
    """Fetch security groups by name.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name of the security group you want to fetch.

    Returns:
        A list of matching security groups.

    """
    params = {}
    params["profile"] = profile
    params["filters"] = [{"Name": "group-name", "Values": [name]}]
    response = utils.do_request(securitygroup, "get", params)
    data = utils.get_data("SecurityGroups", response)
    return data


def fetch(profile, ref):
    """Fetch a security group.

    Args:

        profile
            A profile to connect to AWS with.

        ref
            The name of the security group you want to fetch.

    Returns:
        A list of matching security groups.

    """
    if ref.startswith("sg-"):
        result = fetch_by_id(profile, ref)
    else:
        result = fetch_by_name(profile, ref)
    return result


def is_security_group(profile, ref):
    """Check if a security group exists.

    Args:

        profile
            A profile to connect to AWS with.

        ref
            The name or ID of a security group.

    Returns:
        True if it exists, False if it doesn't.

    """
    result = fetch(profile, ref)
    return len(result) > 0


def polling_fetch(profile, ref, max_attempts=10, wait_interval=1):
    """Try to fetch a security group repeatedly until it exists.

    Args:

        profile
            A profile to connect to AWS with.

        ref
            The name or ID of a security group.

        max_attempts
            The max number of times to poll AWS.

        wait_interval
            How many seconds to wait between each poll.

    Returns:
        The security group's info, or None if it times out.

    """
    data = None
    count = 0
    while count < max_attempts:
        data = fetch(profile, ref)
        if data:
            break
        else:
            count += 1
            sleep(wait_interval)
    if not data:
        msg = "Timed out waiting for security group to be created."
        raise WaitTimedOut(msg)
    return data


def delete_error_handler(error):
    """Handle errors that arise when you delete security groups.

    Args:

        error
            An AWS ``ClientError`` exception.

    Raises:
        ``ResourceHasDependency`` if the security group is dependent
        on another resource, or ``ResourceDoseNotExist`` if the
        security group is gone.

    Returns:
        None, if the error is not worth handling.

    """
    code = error.response["Error"]["Code"]
    if code == "InvalidGroup.NotFound":
        raise ResourceDoesNotExist()
    elif code == "DependencyViolation":
        raise ResourceHasDependency()
    else:
        raise error


def polling_delete(profile, ref, max_attempts=10, wait_interval=1):
    """Try to delete a security group repeatedly until it's gone.

    Args:

        profile
            A profile to connect to AWS with.

        ref
            The name or ID of a security group.

        max_attempts
            The number of times you want to try to delete the group.

        wait_interval
            How many seconds to wait between each deletion attempt.

    Returns:
        True if the security group gets deleted, False if not.

    """
    # Make sure the security group exists.
    sg_id = None
    sg_data = fetch(profile, ref)
    if sg_data:
        sg_id = get_id(sg_data[0])
    else:
        msg = "No security group '" + str(ref) + "'."
        raise ResourceDoesNotExist(msg)
    
    is_deleted = False
    count = 0
    params = {}
    params["profile"] = profile
    params["group_id"] = sg_id
    while count < max_attempts:
        try:
            response = utils.do_request(
                securitygroup,
                "delete",
                params,
                delete_error_handler)
        except ResourceHasDependency:
            pass
        except ResourceDoesNotExist:
            is_deleted = True
        if response:
            is_deleted = True
        if is_deleted:
            break
        else:
            count += 1
            sleep(wait_interval)
    if not is_deleted:
        msg = "Timed out waiting for security group to be deleted."
        raise WaitTimedOut(msg)
    return is_deleted


def create(profile, name, vpc=None, tags=None):
    """Create a security group.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name you want to give to a security group.

        vpc
            The name (or ID) of a VPC to put the security group in.

        tags
            A dict of key/values to add as tags.

    Returns:
        The security group.

    """
    # Check that the VPC exists.
    if vpc:
        vpc_data = vpc_jobs.fetch(profile, vpc)
        if not vpc_data:
            msg = "No VPC '" + str(vpc) + "'."
            raise ResourceDoesNotExist(msg)
        else:
            vpc = vpc_jobs.get_id(vpc_data)

    # Make sure the security group doesn't already exist.
    if is_security_group(profile, name):
        msg = "The security group '" + str(name) + "' already exists."
        raise ResourceAlreadyExists(msg)

    # Now we can create it.
    params = {}
    params["profile"] = profile
    params["name"] = name
    if vpc:
        params["vpc"] = vpc
    response = utils.do_request(securitygroup, "create", params)
    sg_id = utils.get_data("GroupId", response)

    # Now check that it exists.
    sg_data = None
    try:
        sg_data = polling_fetch(profile, sg_id)
    except WaitTimedOut:
        msg = "Timed out waiting for '" + str(name) + "' to be created."
        raise ResourceNotCreated(msg)
    if not sg_data:
        msg = "Security group '" + str(name) + "' not created."
        raise ResourceNotCreated(msg)

    # Now tag the security group.
    if tags:
        for tag in tags:
            params = {}
            params["profile"] = profile
            params["security_group"] = sg_id
            params["key"] = tag["Name"]
            params["value"] = tag["Value"]
            utils.do_request(securitygroup, "tag", params)

    # Send back the group's info.
    return sg_data


def delete(profile, ref, vpc=None):
    """Delete a security group.

    Args:

        profile
            A profile to connect to AWS with.

        ref
            The name (or ID) of the security group you want to delete.

    Returns:
        The security group.

    """
    is_deleted = False
    try:
        is_deleted = polling_delete(profile, ref)
    except ResourceDoesNotExist:
        msg = "No security group '" + str(ref) + "'."
        raise ResourceDoesNotExist(msg)
    except WaitTimedOut:
        msg = "Timed out waiting for '" + str(ref) + "' to be deleted."
        raise ResourceNotDeleted(msg)
    if not is_deleted:
        msg = "Security group '" + str(ref) + "' not deleted."
        raise ResourceNotDeleted(msg)
