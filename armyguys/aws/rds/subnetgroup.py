# -*- coding: utf-8 -*-

"""Utilities for working with RDS DB subnet groups."""

from .. import client as boto3client


def get(profile, group=None):
    """Get DB subnet groups.

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
        params["DBSubnetGroupName"] = group
    return client.describe_db_subnet_groups(**params)


def create(profile, name, subnets, tags=None):
    """Create a DB subnet group.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name you want to give to the group.

        subnets
            A list of subnet IDs to put in the group.

        tags
            A list of {"Key": <key>, "Value": <value>} tags.

    Returns:
        The response returned by boto3.

    """
    client = boto3client.get("rds", profile)
    params = {}
    params["DBSubnetGroupName"] = name
    params["DBSubnetGroupDescription"] = name
    params["SubnetIds"] = subnets
    if tags:
        params["Tags"] = tags
    return client.create_db_subnet_group(**params)


def delete(profile, group):
    """Delete a DB subnet group.

    Args:

        profile
            A profile to connect to AWS with.

        group
            The name of the group you want to delete.

    """
    client = boto3client.get("rds", profile)
    params = {}
    params["DBSubnetGroupName"] = group
    return client.delete_db_subnet_group(**params)
