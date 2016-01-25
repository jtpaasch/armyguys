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

def tag(profile, internet_gateway, key, value):
    """Add a tag to an internet gateway.

    Args:

        profile
            A profile to connect to AWS with.

        internet_gateway
            The ID of the internet gateway you want to tag.

        key
            The key/name of the tag.

        value
            The value of the tag.

    Returns:
        The response returned by boto3.

    """
    client = boto3client.get("ec2", profile)
    params = {}
    params["Resources"] = [internet_gateway]
    params["Tags"] = [{"Key": key, "Value": value}]
    return client.create_tags(**params)

