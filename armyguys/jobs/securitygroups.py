# -*- coding: utf-8 -*-

"""Jobs for security groups."""

from ..aws import securitygroup

from .exceptions import ResourceAlreadyExists
from .exceptions import ResourceDoesNotExist
from .exceptions import ResourceNotCreated

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
            The name of a security group.

    Returns:
        True if it exists, False if it doesn't.

    """
    result = fetch_by_name(profile, ref)
    return len(result) > 0


def create(profile, name, vpc=None):
    """Create a security group.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name you want to give to a security group.

        vpc
            The name (or ID) of a VPC to put the security group in.

    Returns:
        The security group.

    """
    # Check that the VPC is real.
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
    sg_data = fetch(profile, sg_id)
    if not sg_data:
        msg = "Security group '" + str(name) + "' not created."
        raise ResourceNotCreated(msg)
    return sg_data

