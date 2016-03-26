# -*- coding: utf-8 -*-

"""Utilities for working with RDS parameters."""

from .. import client as boto3client


def get(profile, group):
    """Get the parameters for a parameter group.

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
    params["DBParameterGroupName"] = group
    return client.describe_db_parameters(**params)
