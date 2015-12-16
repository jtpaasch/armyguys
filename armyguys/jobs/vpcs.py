# -*- coding: utf-8 -*-

"""Jobs for VPCs."""

from ..aws import vpc

from . import utils


def get_display_name(record):
    """Get the display name for a record.

    Args:

        record
            A record returned by AWS.

    Returns:
        A display name for the VPC.

    """
    ref = get_ref(record)
    if ref.startswith("vpc-"):
        display_name = "Unnamed"
    else:
        display_name = ref
    return display_name + " (" + str(record["VpcId"]) + ")"


def get_ref(record):
    """Get the name of a VPC, or its ID if it has no name.

    Args:

        record
            A VPC record returned by AWS.

    Returns:
        The VPC's name, or its ID if it has no name.

    """
    ref = record["VpcId"]
    tags = record.get("Tags")
    if tags:
        name_tags = [x for x in tags if x["Key"] == "Name"]
        if name_tags:
            ref = name_tags[0]["Value"]
    return ref


def get_id(record):
    """Get the Id out of a VPC record.

    Args:

        record
            A VPC record returned by AWS.

    Returns:
        The VPC's ID.

    """
    return record["VpcId"]


def fetch_all(profile):
    """Fetch all VPCs.

    Args:

        profile
            A profile to connect to AWS with.

    Returns:
        A list of VPCs.

    """
    params = {}
    params["profile"] = profile
    response = utils.do_request(vpc, "get", params)
    data = utils.get_data("Vpcs", response)
    return data


def fetch_by_name(profile, name):
    """Fetch a VPC by name.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name of the VPC you want to fetch.

    Returns:
        A list of VPCs with the provided name.

    """
    params = {}
    params["profile"] = profile
    params["filters"] = [
        {"Name": "tag-key", "Values": ["Name"]},
        {"Name": "tag-value", "Values": [name]},
        ]
    response = utils.do_request(vpc, "get", params)
    data = utils.get_data("Vpcs", response)
    return data


def fetch_by_id(profile, vpc_id):
    """Fetch a VPC by id.

    Args:

        profile
            A profile to connect to AWS with.

        vpc_id
            The ID of the VPC you want to fetch.

    Returns:
        A list of VPCs with the provided ID.

    """
    params = {}
    params["profile"] = profile
    params["filters"] = [{"Name": "vpc-id", "Values": [vpc_id]}]
    response = utils.do_request(vpc, "get", params)
    data = utils.get_data("Vpcs", response)
    return data


def fetch(profile, ref):
    """Fetch a VPC.

    Args:

        profile
            A profile to connect to AWS with.

        ref
            The name or ID of the VPC you want to fetch.

    Returns:
        A list of VPC records.

    """
    if ref.startswith("vpc-"):
        result = fetch_by_id(profile, ref)
    else:
        result = fetch_by_name(profile, ref)
    return result


def is_vpc(profile, ref):
    """Check if a VPC exists.

    Args:

        profile
            A profile to connect to AWS with.

        ref
            The name or ID of a VPC.

    Returns:
        True if it exists, False if it doesn't.

    """
    result = fetch(profile, ref)
    return len(result) > 0
