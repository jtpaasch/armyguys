# -*- coding: utf-8 -*-

"""Utilities for using/loading an AWS profile.

An AWS profile includes credentials to connect with, and a region.
Every boto3 request requires credentials and a region.

"""

from os import path
from boto3.session import Session


def ephemeral(access_key_id, secret_access_key, region_name="us-east-1"):
    """Create a profile in memory (don't save it on disk).

    Args:

        access_key_id
            An AWS access key Id provided by Amazon for an AWS user.

        secret_access_key
            An AWS secret access key provided by Amazon for an AWS user.

        region_name
            An AWS region.

    Returns:
        An instance of a boto3 session, configured with the specified params.

    """
    session = Session(aws_access_key_id=access_key_id,
                      aws_secret_access_key=secret_access_key,
                      region_name=region_name)
    return session


def configured(profile_name="default"):
    """Load a pre-configured profile (stored at ~/.aws/credentials).

    Args:

        profile_name
            The name of a profile to use. This name must match one
            of the profiles in ~/.aws/credentials.

    Returns:
        An instance of a boto3 session, configured with the named profile.

    """
    session = Session(profile_name=profile_name)
    return session
