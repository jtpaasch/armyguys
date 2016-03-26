# -*- coding: utf-8 -*-

"""Utilities for working with IAM policies."""

import json
from os import path
from .. import client as boto3client


def create(profile, name, contents=None, filepath=None):
    """Create an IAM policy (from a file).

    Args:

        profile
            A profile to connect to AWS with.

        name
            A name to give to the policy.

        contents
            The contents of the policy (as a Python dict or list).
            You must specify this OR a filepath.

        filepath
            The path to the policy you want to upload.
            You must specify this OR a filepath.

    Returns:
        The response returned by boto3.

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
    params["PolicyName"] = name
    params["PolicyDocument"] = data
    return client.create_policy(**params)


def delete(profile, policy):
    """Delete an IAM policy.

    Args:

        profile
            A profile to connect to AWS with.

        policy
            The full ARN of the policy you want to delete.

    """
    client = boto3client.get("iam", profile)
    params = {}
    params["PolicyArn"] = policy
    return client.delete_policy(**params)


def get(profile):
    """Get a list of all IAM policies.

    Args:

        profile
            A profile to connect to AWS with.

    Returns:
        The response returned by boto3.

    """
    client = boto3client.get("iam", profile)
    return client.list_policies()


def details(profile, policy):
    """Get one IAM policy.

    Args:

        profile
            A profile to connect to AWS with.

        policy
            The ARN of the policy you want to fetch.

    Returns:
        The response returned by boto3.

    """
    client = boto3client.get("iam", profile)
    params = {}
    params["PolicyArn"] = policy
    return client.get_policy(**params)

