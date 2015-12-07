# -*- coding: utf-8 -*-

"""Utilities for fetching availaibility zone info."""

from ...aws import availabilityzone

ZONE_BLACKLIST = ["us-east-1a"]


def get_all(profile):
    """Get all availability zones.

    Args:

        profile
            A profile to connect to AWS with.

    Return:
        The data returned by AWS, or None if
        no availability zones were found.

    """
    params = {}
    params["profile"] = profile
    response = availabilityzone.get(**params)
    data = response.get("AvailabilityZones")
    result = None
    if len(data) > 0:
        result = [x for x in data if x["ZoneName"] not in ZONE_BLACKLIST]
    return result
