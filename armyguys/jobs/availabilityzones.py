# -*- coding: utf-8 -*-

"""Jobs for availability zones."""

from ..aws import availabilityzone

from . import utils


# Some zones are currently unavailable in AWS.
# We want to ignore them.
ZONE_BLACKLIST = ["us-east-1a"]


def fetch_all(profile):
    """Fetch all availability zones.

    Args:

        profile
            A profile to connect to AWS with.

    Returns:
        A list of zones.

    """
    params = {}
    params["profile"] = profile
    response = utils.do_request(availabilityzone, "get", params)
    data = utils.get_data("AvailabilityZones", response)
    return [x for x in data if x["ZoneName"] not in ZONE_BLACKLIST]
 

def fetch_by_name(profile, name):
    """Fetch availability zones by name.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name of an availability zone.

    Returns:
        A list of zones with the specified name.

    """
    params = {}
    params["profile"] = profile
    params["filters"] = [{"Name": "zone-name", "Values": [name]}]
    response = utils.do_request(availabilityzone, "get", params)
    data = utils.get_data("AvailabilityZones", response)
    return [x for x in data if x["ZoneName"] not in ZONE_BLACKLIST]


def is_zone(profile, ref):
    """Check if an availability zone exists.

    Args:

        profile
            A profile to connect to AWS with.

        ref
            The name of an availability zone.

    Returns:
        True if it exists. False if not.

    """
    records = fetch_by_name(profile, ref)
    return len(records) > 0
