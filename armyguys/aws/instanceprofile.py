# -*- coding: utf-8 -*-

"""Utilities for working with IAM instance profiles."""

from . import client as boto3client


def create(profile, name):
    """Create an IAM instance profile.

    Args:

        profile
            A profile to connect to AWS with.

        name
            A name to give to the instance profile.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("iam", profile)
    params = {}
    params["InstanceProfileName"] = name
    return client.create_instance_profile(**params)


def delete(profile, name):
    """Delete an IAM instance profile.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name of the instance profile you want to delete.

    """
    client = boto3client.get("iam", profile)
    params = {}
    params["InstanceProfileName"] = name
    return client.delete_instance_profile(**params)


def get(profile):
    """Get a list of all IAM instance profiles.

    Args:

        profile
            A profile to connect to AWS with.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("iam", profile)
    return client.list_instance_profiles()


def add_role(profile, instance_profile, role):
    """Add a role to an instance profile.

    Args:

        profile
            A profile to connect to AWS with.

        instance_profile
            The name of the instance profile you want to add the role to.

        role
            The name of the role you want to add.

    """
    client = boto3client.get("iam", profile)
    params = {}
    params["InstanceProfileName"] = instance_profile
    params["RoleName"] = role
    return client.add_role_to_instance_profile(**params)


def remove_role(profile, instance_profile, role):
    """Remove a role from an instance profile.

    Args:

        profile
            A profile to connect to AWS with.

        instance_profile
            The name of the instance profile you want to remove a role from.

        role
            The name of the role you want to remove.

    """
    client = boto3client.get("iam", profile)
    params = {}
    params["InstanceProfileName"] = instance_profile
    params["RoleName"] = role
    return client.remove_role_from_instance_profile(**params)
