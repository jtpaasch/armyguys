# -*- coding: utf-8 -*-

"""Jobs for subnets."""

from ..aws import subnet

from .exceptions import WaitTimedOut
from .exceptions import ResourceAlreadyExists
from .exceptions import ResourceDoesNotExist
from .exceptions import ResourceNotCreated
from .exceptions import ResourceNotDeleted

from . import vpcs as vpc_jobs
from . import availabilityzones as zone_jobs

from . import utils


def get_display_name(record):
    """Get the display name for a record.

    Args:

        record
            A record returned by AWS.

    Returns:
        A display name for the subnet.

    """
    subnet_id = get_id(record)
    ref = get_ref(record)
    if ref.startswith("subnet-"):
        if record["DefaultForAz"]:
            display_name = "Default"
        else:
            display_name = "Unnamed"
    else:
        display_name = ref
    return display_name + " (" + str(subnet_id) + ")"


def get_ref(record):
    """Get the name of the subnet, or its ID if it has no name.

    Args:

        record
            A record returned by AWS

    Returns:
        The subnet's name, or its ID if it has no name.

    """
    ref = record["SubnetId"]
    tags = record.get("Tags")
    if tags:
        name_tags = [x for x in tags if x["Key"] == "Name"]
        if name_tags:
            ref = name_tags[0]["Value"]
    return ref


def get_id(record):
    """Get the ID from a record.

    Args:

        record
            A record returned by AWS.

    Returns:
        The ID of the subnet.

    """
    return record["SubnetId"]


def fetch_all(profile):
    """Fetch all subnets.

    Args:

        profile
            A profile to connect to AWS with.

    Returns:
        A list of subnets.

    """
    params = {}
    params["profile"] = profile
    response = utils.do_request(subnet, "get", params)
    data = utils.get_data("Subnets", response)
    return data


def fetch_by_name(profile, name):
    """Fetch a subnet by name.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name of a subnet.

    Returns:
        A list of subnets that match.

    """
    params = {}
    params["profile"] = profile
    params["filters"] = [
        {"Name": "tag-key", "Values": ["Name"]},
        {"Name": "tag-value", "Values": [name]},
        ]
    response = utils.do_request(subnet, "get", params)
    data = utils.get_data("Subnets", response)
    return data


def fetch_by_id(profile, subnet_id):
    """Fetch a subnet by id.

    Args:

        profile
            A profile to connect to AWS with.

        subnet_id
            The ID of a subnet.

    Returns:
        A list of subnets that match.

    """
    params = {}
    params["profile"] = profile
    params["filters"] = [{"Name": "subnet-id", "Values": [subnet_id]}]
    response = utils.do_request(subnet, "get", params)
    data = utils.get_data("Subnets", response)
    return data


def fetch(profile, ref):
    """Fetch a particular subnet.

    Args:

        profile
            A profile to connect to AWS with.

        ref
            The name or ID of a subnet.

    Returns:
        A list of subnets that match.

    """
    if ref.startswith("subnet-"):
        result = fetch_by_id(profile, ref)
    else:
        result = fetch_by_name(profile, ref)
    return result


def fetch_by_vpc(profile, vpc):
    """Fetch subnets in a VPC.

    Args:

        profile
            A profile to connect to AWS with.

        vpc
            The name or ID of a VPC.

    Returns:
        A list of subnets in the VPC.

    """
    # Make sure the VPC exists.
    vpc_data = vpc_jobs.fetch(profile, vpc)
    if vpc_data:
        vpc_id = vpc_jobs.get_id(vpc_data[0])
    else:
        msg = "No VPC '" + str(vpc) + "'."
        raise ResourceDoesNotExist(msg)

    # Fetch the subnets for that VPC.
    params = {}
    params["profile"] = profile
    params["filters"] = [{"Name": "vpc-id", "Values": [vpc_id]}]
    response = utils.do_request(subnet, "get", params)
    data = utils.get_data("Subnets", response)
    return data


def is_subnet(profile, ref):
    """Check if a subnet exists.

    Args:

        profile
            A profile to connect to AWS with.

        ref
            The ID of a subnet.

    Returns:
        True if it exists, False if it doesn't.

    """
    result = fetch(profile, ref)
    return len(result) > 0


def polling_fetch(profile, ref, max_attempts=10, wait_interval=1):
    """Try to fetch a subnet repeatedly until it exists.

    Args:

        profile
            A profile to connect to AWS with.

        ref
            The ID of the subnet you want to fetch.

        max_attempts
            The max number of times to poll AWS.

        wait_interval
            How many seconds to wait between each poll.

    Returns:
        The subnet's info, or None if it times out.

    """
    data = None
    count = 0
    while count < max_attempts:
        data = fetch(profile, ref)
        if data:
            break
        else:
            count += 1
            sleep(wait_interval)
    if not data:
        msg = "Timed out waiting for subnet to be created."
        raise WaitTimedOut(msg)
    return data


def create(profile, name, vpc, cidr_block, zone=None, tags=None):
    """Create a subnet.

    Args:

        profile
            A profile to connect to AWS with.

        name
            A name to give to the subnet.

        vpc
            The name or ID of the VPC.

        cidr_block
            The CIDR network range of the subnet.

        zone
            The availability zone to put the subnet in.

        tags
            A dict of key/values to add as tags.

    Returns:
        The newly created subnet's info.

    """
    # Make sure the VPC exists.
    vpc_data = vpc_jobs.fetch(profile, vpc)
    if vpc_data:
        vpc_id = vpc_jobs.get_id(vpc_data[0])
    else:
        msg = "No VPC '" + str(vpc) + "'."
        raise ResourceDoesNotExist(msg)

    # Make sure the availability zone exists.
    if zone:
        if not zone_jobs.is_zone(profile, zone):
            msg = "No availability zone '" + str(zone) + "'."
            raise ResourceDoesNotExist(msg)

    # Make sure the subnet doesn't exist.
    if is_subnet(profile, name):
        msg = "Subnet '" + str(name) + "' already exists."
        raise ResourceAlreadyExists(msg)

    # Add the name to the list of tags.
    if not tags:
        tags = []
    tags.append({"Key": "Name", "Value": name})

    # Now create it.
    params = {}
    params["profile"] = profile
    params["vpc"] = vpc_id
    params["cidr_block"] = cidr_block
    if zone:
        params["availability_zone"] = zone
    response = utils.do_request(subnet, "create", params)
    data = utils.get_data("Subnet", response)
    ref = data["SubnetId"]

    # Now check that it exists.
    subnet_data = None
    try:
        subnet_data = polling_fetch(profile, ref)
    except WaitTimedOut:
        msg = "Timed out waiting for " + str(cidr) + " subnet to be created."
        raise ResourceNotCreated(msg)
    if not subnet_data:
        msg = "Subnet for " + str(cidr) + " not created."
        raise ResourceNotCreated(msg)

    # Now tag it with all the tags.
    subnet_id = get_id(subnet_data[0])
    if tags:
        for tag in tags:
            params = {}
            params["profile"] = profile
            params["subnet"] = subnet_id
            params["key"] = tag["Key"]
            params["value"] = tag["Value"]
            utils.do_request(subnet, "tag", params)

    # Get its data again (this time with tags).
    subnet_data = fetch(profile, ref)

    # Send back the subnet's data.
    return subnet_data


def delete(profile, ref):
    """Delete a subnet.

    Args:

        profile
            A profile to connect to AWS with.

        ref
            The name or ID of a subnet.

    """
    # Make sure it exists before we try to delete it.
    subnet_data = fetch(profile, ref)
    if not subnet_data:
        msg = "No subnet '" + str(ref) + "'."
        raise ResourceDoesNotExist(msg)
    else:
        subnet_id = get_id(subnet_data[0])

    # Now try to delete it.
    params = {}
    params["profile"] = profile
    params["subnet"] = subnet_id
    response = utils.do_request(subnet, "delete", params)

    # Check that it was, in fact, deleted.
    if is_subnet(profile, ref):
        msg = "Subnet '" + str(name) + "' was not deleted."
        raise ResourceNotDeleted(msg)
