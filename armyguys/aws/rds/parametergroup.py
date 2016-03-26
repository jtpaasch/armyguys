# -*- coding: utf-8 -*-

"""Utilities for working with RDS parameter groups."""

from .. import client as boto3client


def get(profile, group=None):
    """Get a list of parameter groups.

    Args:

        profile
            A profile to connect to AWS with.

        group
            The name of a group you want to get.

    Returns:
        The response returned by boto3.

    """
    client = boto3client.get("rds", profile)
    params = {}
    if group:
        params["DBParameterGroupName"] = group
    return client.describe_db_parameter_groups(**params)


def create(profile, name, family, tags=None):
    """Create an empty parameter group.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name you want to give to the group.

        family
            The parameter group family, e.g., "mysql5.7."

        tags
            A list of {"Key": <key>, "Value": <value>} tags.

    Returns:
        The response returned by boto3.

    """
    client = boto3client.get("rds", profile)
    params = {}
    params["DBParameterGroupName"] = name
    params["DBParameterGroupFamily"] = family
    params["Description"] = name
    if tags:
        params["Tags"] = tags
    return client.create_db_parameter_group(**params)


def delete(profile, group):
    """Delete a parameter group.

    Args:

        profile
            A profile to connect to AWS with.

        group
            The name of the group you want to delete.

    Returns:
        The response returned by boto3.

    """
    client = boto3client.get("rds", profile)
    params = {}
    params["DBParameterGroupName"] = group
    return client.delete_db_parameter_group(**params)


def modify(profile, group, parameters):
    """Modify a parameter group.

    Args:

        profile
            A profile to connect to AWS with.

        group
            The name of the group you want to delete.

        parameters
            A list of parameter objects that look like this::

            {
                "ParameterName": <name>,
                "ParameterValue": <name>,
                "ApplyMethod": "immediate|pending-reboot",
                ...
            }

    Returns:
        The response returned by boto3.

    """
    client = boto3client.get("rds", profile)
    params = {}
    params["DBParameterGroupName"] = group
    params["Parameters"] = parameters
    return client.modify_db_parameter_group(**params)
