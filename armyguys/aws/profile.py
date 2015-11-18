# -*- coding: utf-8 -*-

"""Utilities for using/loading an AWS profile.

An AWS profile includes credentials to connect with, and a region.
Every boto3 request requires credentials and a region.

"""

from os import path
from boto3.session import Session

try:
    import configparser
except ImportError:
    import ConfigParser as configparser


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
    """Load a pre-configured profile (stored at ~/.aws/{credentials,config}).

    Note:
        The credentials are stored in ~/.aws/credentials, and the region is
        stored in ~/.aws/config. If no region is specified for the requested
        profile in ~/.aws/config, then the default region is used. If no
        default region is specified, then "us-east-1" is used.

    Args:

        profile_name
            The name of a profile to use. This name must match one
            of the profiles in ~/.aws/credentials.

    Returns:
        An instance of a boto3 session, configured with the named profile.

    """
    region = get_region(profile_name=profile_name)
    if not region:
        region = get_region(profile_name="default")
        if not region:
            region = "us-east-1"
    session = Session(profile_name=profile_name, region_name=region)
    return session


def get_config(profile_name):
    """Get data for a profile from ~/.aws/config.

    Args:

        profile_name
            The name of the section to get from ~/.aws/config.

    Returns:
        The config section, or None.

    """
    config = configparser.ConfigParser()
    filepath = path.expanduser("~/.aws/config")
    config.read(filepath)
    result = None
    if profile_name in config:
        result = config[profile_name]
    return result


def get_region(profile_name):
    """Get a region for a profile in ~/.aws/config.

    Args:

        profile_name
           The name of the profile to get the region from
           in ~/.aws/config.

    Returns:
        The specified region, e.g., "us-east-1", or None.

    """
    config_data = get_config(profile_name)
    result = None
    if config_data:
        result = config_data.get("region")
    return result
