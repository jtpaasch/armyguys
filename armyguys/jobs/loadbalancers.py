# -*- coding: utf-8 -*-

"""Jobs for load balancers."""

from time import sleep

from botocore.exceptions import ClientError

from ..aws import loadbalancer

from . import launchconfigurations as launchconfig_jobs
from . import regions as region_jobs
from . import securitygroups as sg_jobs

from .exceptions import ResourceAlreadyExists
from .exceptions import ResourceDoesNotExist
from .exceptions import ResourceHasDependency
from .exceptions import ResourceNotCreated
from .exceptions import ResourceNotDeleted
from .exceptions import WaitTimedOut

from . import utils


def get_display_name(record):
    """Get the display name for a record.

    Args:

        record
            A record returned by AWS.

    Returns:
        A display name for the load balancer.

    """
    return record["LoadBalancerName"] + " (" + record["DNSName"] + ")"


def fetch_all(profile):
    """Fetch all load balancers.

    Args:

        profile
            A profile to connect to AWS with.

    Returns:
        A list of load balancers.

    """
    params = {}
    params["profile"] = profile
    response = utils.do_request(loadbalancer, "get", params)
    data = utils.get_data("LoadBalancerDescriptions", response)
    return data


def fetch_by_name(profile, name):
    """Fetch a load balancer by name.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name of a load balancer.

    Returns:
        A list of matching load balancers.

    """
    params = {}
    params["profile"] = profile
    params["load_balancer"] = name
    response = utils.do_request(loadbalancer, "get", params)
    data = []
    if response:
        data = utils.get_data("LoadBalancerDescriptions", response)
    return data


def exists(profile, name):
    """Check if a load balancer exists.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name of a load balancer.

    Returns:
        True if it exists, False if it doesn't.

    """
    result = fetch_by_name(profile, name)
    return len(result) > 0


def polling_fetch_by_name(profile, name, max_attempts=10, wait_interval=1):
    """Try to fetch a load balancer repeatedly.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name of a load balancer

        max_attempts
            The max number of times to poll AWS.

        wait_interval
            How many seconds to wait between each poll.

    Returns:
        The load balancer's info, or None if it times out.

    """
    data = None
    count = 0
    while count < max_attempts:
        data = fetch_by_name(profile, name)
        if data:
            break
        else:
            count += 1
            sleep(wait_interval)
    if not data:
        msg = "Timed out waiting for load balancer to be created."
        raise WaitTimedOut(msg)
    return data


def polling_is_deleted(profile, name, max_attempts=10, wait_interval=1):
    """Repeatedly check if a load balancer is deleted.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name of an auto scaling group.

        max_attempts
            The max number of times to poll AWS.

        wait_interval
            How many seconds to wait between each poll.

    Returns:
        The load balancer's info, if any was returned.

    """
    data = None
    count = 0
    while count < max_attempts:
        data = fetch_by_name(profile, name)
        if not data:
            break
        else:
            count += 1
            sleep(wait_interval)
    if data:
        msg = "Timed out waiting for load balancer to be deleted."
        raise WaitTimedOut(msg)
    return data


def create(
        profile,
        name,
        listeners=None,
        security_groups=None,
        availability_zones=None,
        subnets=None,
        vpc=None,
        tags=None):
    """Create an auto scaling group.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name you want to give to a security group.

        listeners
            A list of dicts with this form::

                {
                    "Protocol": "HTTP",
                    "LoadBalancerPort": 80,
                    "InstanceProtocol": "HTTP",
                    "InstancePort": 80,
                    "SSLCertificateId": None,
                }

        security_groups
            A list of security groups for the load balancer.

        availability_zones
            A list of availability zones to launch the load balancer in.

        subnets
            A list of subnets to launch the load balancer in.

        vpc
            A VPC to launch the load balancer in.

        tags
            A list of {"Key": key, "Value": value} dicts.

    Returns:
        The load balancer's info.

    """
    # Make sure the load balancer doesn't already exist.
    if exists(profile, name):
        msg = "Load balancer '" + str(name) + "' already exists."
        raise ResourceAlreadyExists(msg)

    # Make sure the security groups exist.
    security_group_ids = []
    if security_groups:
        for security_group in security_groups:
            security_group_data = sg_jobs.fetch(profile, security_group)
            if security_group_data:
                sg_id = sg_jobs.get_id(security_group_data[0])
                security_group_ids.append(sg_id)
            else:
                msg = "No security group '" + str(security_group) + "'."
                raise ResourceDoesNotExist(msg)
    
    # Get the availability zones/subnets we want to delpoy into.
    sub_regions = region_jobs.get_available_sub_regions(
        profile,
        vpc,
        subnets,
        availability_zones)
    
    # Now we can create it.
    params = {}
    params["profile"] = profile
    params["name"] = name
    params["listeners"] = listeners
    if security_group_ids:
        params["security_groups"] = security_group_ids
    params["availability_zones"] = sub_regions["availability_zones"]
    params["subnets"] = sub_regions["subnets"]
    response = utils.do_request(loadbalancer, "create", params)

    # Now check that it exists.
    load_balancer_data = None
    try:
        load_balancer_data = polling_fetch_by_name(profile, name)
    except WaitTimedOut:
        msg = "Timed out waiting for '" + str(name) + "' to be created."
        raise ResourceNotCreated(msg)
    if not load_balancer_data:
        msg = "Load balancer '" + str(name) + "' not created."
        raise ResourceNotCreated(msg)

    # Tag the load balancer.
    if tags:
        for tag in tags:
            params = {}
            params["profile"] = profile
            params["load_balancer"] = name
            params["key"] = tag["Key"]
            params["value"] = tag["Value"]
            utils.do_request(loadbalancer, "tag", params)
    
    # Send back the load balancer's info.
    return load_balancer_data


def delete(profile, name):
    """Delete a load balancer.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name of a load balancer.

    """
    # Make sure it exists before we try to delete it.
    load_balancer_data = fetch_by_name(profile, name)
    if not load_balancer_data:
        msg = "No load balancer '" + str(name) + "'."
        raise ResourceDoesNotExist(msg)

    # Now try to delete it.
    params = {}
    params["profile"] = profile
    params["load_balancer"] = name
    response = utils.do_request(loadbalancer, "delete", params)

    # Check that it was, in fact, deleted.
    is_deleted = polling_is_deleted(profile, name)
    load_balancer_data = fetch_by_name(profile, name)
    if load_balancer_data:
        msg = "Load balancer '" + str(name) + "' was not deleted."
        raise ResourceNotDeleted(msg)
