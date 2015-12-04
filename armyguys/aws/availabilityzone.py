# -*- coding: utf-8 -*-

"""Utilities for working with VPC availability zones."""

from . import client as boto3client


def get(profile, filters=None):
    """Get a list of all availability zones for the profile.

    Args:

        profile
            A profile to connect to AWS with.

        filters
            Filters to apply to the request.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("ec2", profile)
    params = {}
    if filters:
        params["Filters"] = filters
    return client.describe_availability_zones(**params)
