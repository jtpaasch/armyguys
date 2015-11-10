# -*- coding: utf-8 -*-

"""Utilities for working with internet gateways."""

from . import client as boto3client


def create(profile):
    """Create an internet gateway.

    Args:

        profile
            A profile to connect to AWS with.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("ec2", profile)
    return client.create_internet_gateway()


def delete(profile):
    """Delete an internet gateway.

    Args:

        profile
            A profile to connect to AWS with.

    """
    client = boto3client.get("ec2", profile)
    params = {}
    params["InternetGatewayId"] = vpc
    return client.delete_internet_gateway(**params)


def get(profile):
    """Get a list of all internet gateways.

    Args:

        profile
            A profile to connect to AWS with.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("ec2", profile)
    return client.describe_internet_gateways()
