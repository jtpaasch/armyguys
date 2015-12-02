# -*- coding: utf-8 -*-

"""Utilities for working with Route 53 resource record sets."""

from . import client as boto3client


def get(profile, dns_name=None):
    """Get all record sets in a hosted zone.

    Args:

        profile
            A profile to connect to AWS with.

        dns_name
            The DNS name of a hosted zone you want to get
            record sets for.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("route53", profile)
    params = {}
    params["HostedZoneId"] = dns_name
    return client.list_resource_record_sets(**params)
