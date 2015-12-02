# -*- coding: utf-8 -*-

"""Utilities for working with Route 53 hosted zones."""

from . import client as boto3client


def get(profile, dns_name=None):
    """Get all hosted zones, or a specific one.

    Args:

        profile
            A profile to connect to AWS with.

        dns_name
            The DNS name of a hosted zone you want to get.
            If you omit this, all zones are returned.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("route53", profile)
    params = {}
    if dns_name:
        params["DNSName"] = dns_name
    return client.list_hosted_zones_by_name(**params)
