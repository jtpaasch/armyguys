# -*- coding: utf-8 -*-

"""Utilities for working with IAM roles."""

import json
from os import path
from . import client as boto3client


def create(profile, name, contents=None, filepath=None):
    """Create an IAM role.

    Args:

        profile
            A profile to connect to AWS with.

        name
            A name to give to the policy.

        contents
            The policy contents (as a Python dict or list).
            You must specify this OR a filepath.

        filepath
            The path to the trust policy you want to upload.
            You must specify this OR a filepath.

    Returns:
        The JSON response returned by boto3.

    """
    if filepath:
        norm_path = path.normpath(filepath)
        norm_path = norm_path.rstrip(path.sep)
        with open(norm_path, "rb") as f:
            data = f.read().decode("utf-8")
    elif contents:
        data = json.dumps(contents)
    client = boto3client.get("iam", profile)
    params = {}
    params["RoleName"] = name
    params["AssumeRolePolicyDocument"] = data
    return client.create_role(**params)


def delete(profile, role):
    """Delete an IAM role.

    Args:

        profile
            A profile to connect to AWS with.

        role
            The name of the role you want to delete.

    """
    client = boto3client.get("iam", profile)
    params = {}
    params["RoleName"] = role
    return client.delete_role(**params)


def get(profile):
    """Get a list of all IAM roles.

    Args:

        profile
            A profile to connect to AWS with.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("iam", profile)
    return client.list_roles()


def attach_policy(profile, role, policy):
    """Attach a policy to an IAM role.

    Args:

        profile
            A profile to connect to AWS with.

        role
            The name of the role you want to attach a policy to.

        policy
            The ARN of the policy you want to attach.

    """
    client = boto3client.get("iam", profile)
    params = {}
    params["RoleName"] = role
    params["PolicyArn"] = policy
    return client.attach_role_policy(**params)


def detach_policy(profile, role, policy):
    """Detach a policy to an IAM role.

    Args:

        profile
            A profile to connect to AWS with.

        role
            The name of the role you want to detach a policy from.

        policy
            The ARN of the policy you want to detach.

    """
    client = boto3client.get("iam", profile)
    params = {}
    params["RoleName"] = role
    params["PolicyArn"] = policy
    return client.detach_role_policy(**params)
