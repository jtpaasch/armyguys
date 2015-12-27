# -*- coding: utf-8 -*-

"""Utilities for working with the user's account."""

from . import client as boto3client


def get(profile):
    """Get data on the user.

    Args:

        profile
            A profile to connect to AWS with.

    Returns:
        The data returned by boto3.

    """
    client = boto3client.get("iam", profile)
    return client.get_user()
