# -*- coding: utf-8 -*-

"""Utilities for working with IAM resources."""

from os import path
from . import client as boto3client


def create_policy(profile, name, filepath):
    """Create an IAM policy.

    Args:

        profile
            A profile to connect to AWS with.

        name
            A name to give to the policy.

        filepath
            The path to the file you want to upload.

    Returns:
        The JSON response returned by boto3.

    """
    norm_path = path.normpath(filepath)
    norm_path = norm_path.rstrip(path.sep)
    with open(norm_path, "rb") as f:
        data = f.read().decode("utf-8")
    client = boto3client.get("iam", profile)
    params = {}
    params["PolicyName"] = name
    params["PolicyDocument"] = data
    return client.create_policy(**params)


def delete_policy(profile, policy_arn):
    """Delete an IAM policy.

    Args:

        profile
            A profile to connect to AWS with.

        policy_ARN
            The full ARN of the policy you want to delete.

    """
    client = boto3client.get("iam", profile)
    params = {}
    params["PolicyArn"] = policy_arn
    return client.delete_policy(**params)
