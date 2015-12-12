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
 
