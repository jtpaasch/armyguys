# -*- coding: utf-8 -*-

"""Utilities for fetching availaibility zone info."""

from ...aws import availabilityzone


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
        result = data
    return result
