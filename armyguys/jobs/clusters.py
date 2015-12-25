# -*- coding: utf-8 -*-

"""Jobs for ECS clusters."""

from time import sleep

from botocore.exceptions import ClientError

from ..aws.ecs import cluster

from . import availabilityzones as zone_jobs
from . import launchconfigurations as launchconfig_jobs
from . import loadbalancers as loadbalancer_jobs
from . import regions as region_jobs

from .exceptions import ResourceAlreadyExists
from .exceptions import ResourceDoesNotExist
from .exceptions import ResourceHasDependency
from .exceptions import ResourceNotCreated
from .exceptions import ResourceNotDeleted
from .exceptions import WaitTimedOut

from . import autoscalinggroups as scalinggroup_jobs
from . import launchconfigurations as launchconfig_jobs
from . import regions as region_jobs

from . import utils


def get_auto_scaling_group_name(cluster):
    """Get the name for a cluster's auto scaling group.

    Args:

        cluster
            The name of a cluster.

    Returns:
        The auto scaling group's name.

    """
    return str(cluster) + "--ecs-cluster-auto-scaling-group"


def get_launch_config_name(cluster):
    """Get the name for a cluster's launch configuration.

    Args:

        cluster
            The name of a cluster.

    Returns:
        The launch configuration's name.

    """
    return str(cluster) + "--ecs-cluster-launch-configuration"


def get_display_name(record):
    """Get the display name for a record.

    Args:

        record
            A record returned by AWS.

    Returns:
        A display name for the cluster.

    """
    return record["clusterName"]


def fetch_all(profile):
    """Fetch all clusters.

    Args:

        profile
            A profile to connect to AWS with.

    Returns:
        A list of clusters.

    """
    params = {}
    params["profile"] = profile
    response = utils.do_request(cluster, "get", params)
    data = utils.get_data("clusters", response)
    return [x for x in data if x["status"] == "ACTIVE"]


def fetch_by_name(profile, name):
    """Fetch auto scaling groups by name.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name of the cluster you want to fetch.

    Returns:
        A list of matching clusters.

    """
    params = {}
    params["profile"] = profile
    params["cluster"] = name
    response = utils.do_request(cluster, "get", params)
    data = utils.get_data("clusters", response)
    return [x for x in data if x["status"] == "ACTIVE"]


def exists(profile, name):
    """Check if a cluster exists.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name of a cluster.

    Returns:
        True if it exists, False if it doesn't.

    """
    result = fetch_by_name(profile, name)
    status = None
    if len(result) > 0:
        status = result[0]["status"]
    return status == "ACTIVE"


def polling_fetch(profile, name, max_attempts=10, wait_interval=1):
    """Try to fetch a cluster repeatedly until you get it.

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
        The cluster's info, or None if it times out.

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
        msg = "Timed out waiting for cluster to be created."
        raise WaitTimedOut(msg)
    return data


def polling_is_deleted(profile, name, max_attempts=10, wait_interval=1):
    """Repeatedly check if a cluster is deleted.

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
        The cluster's info, if any was returned.

    """
    is_deleted = False
    count = 0
    while count < max_attempts:
        is_deleted = not exists(profile, name)
        if is_deleted:
            break
        else:
            count += 1
            sleep(wait_interval)
    if not is_deleted:
        msg = "Timed out waiting for cluster to be deleted."
        raise WaitTimedOut(msg)
    return is_deleted


def create(
        profile,
        name,
        instance_type=None,
        key_pair=None,
        security_groups=None,
        instance_profile=None,
        user_data_files=None,
        min_size=None,
        max_size=None,
        desired_size=None,
        availability_zones=None,
        subnets=None,
        vpc=None,
        tags=None):
    """Create an ECS cluster.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name you want to give to the cluster.

        key_pair
            The name of a key pair to use.

        security_groups
            A list of security group names or IDs.

        instance_profile
            The name of an instance profile for the EC2 instances.

        user_data_files
            A list of {"filepath": path, "contenttype": type} entries
            to make into a Mime Multi Part Archive for user data.

        min_size
            The minimum number of EC2 instances to keep in the cluster.

        max_size
            The maximum number of EC2 instances to keep in the cluster.

        desired_size
            The ideal number of EC2 instances to keep in the cluster.

        availability_zones
            A list of availability zones to launch the cluster in.

        subnets
            A list of subnets to launch the cluster in.

        vpc
            A VPC to launch into.

        tags
            A list of key/values to add as tags.

    Returns:
        The cluster's info.

    """
    auto_scaling_group_name = get_auto_scaling_group_name(name)
    launch_config_name = get_launch_config_name(name)

    # Add a tag indicating which ECS cluster this is all for.
    if not tags:
        tags = []
    tags.append({"Key": "ECS Cluster", "Value": name})

    # Make sure the cluster doesn't already exist.
    if exists(profile, name):
        msg = "The cluster '" + str(name) + "' already exists."
        raise ResourceAlreadyExists(msg)

    # Make sure the launch config doesn't already exist.
    if launchconfig_jobs.exists(profile, launch_config_name):
        msg = "A launch config '" + str(launch_config_name) \
              + "' already exists."
        raise ResourceAlreadyExists(msg)

    # Make sure the auto scaling group doesn't already exist.
    if scalinggroup_jobs.exists(profile, auto_scaling_group_name):
        msg = "An auto scaling group '" + str(auto_scaling_group_name) \
              + "' already exists."
        raise ResourceAlreadyExists(msg)

    # Create the launch configuration.
    params = {}
    params["profile"] = profile
    params["name"] = launch_config_name
    if instance_type:
        params["instance_type"] = instance_type
    params["key_pair"] = key_pair
    params["instance_profile"] = instance_profile
    params["user_data_files"] = user_data_files
    params["security_groups"] = security_groups
    params["public_ip"] = True
    launchconfig_jobs.create(**params)

    # Create the auto scaling group.
    params = {}
    params["profile"] = profile
    params["name"] = auto_scaling_group_name
    params["launch_configuration"] = launch_config_name
    if min_size:
        params["min_size"] = min_size
    if max_size:
        params["max_size"] = max_size
    if desired_size:
        params["desired_size"] = desired_size
    params["availability_zones"] = availability_zones
    params["subnets"] = subnets
    params["vpc"] = vpc
    params["tags"] = tags
    scalinggroup_jobs.create(**params)

    # Create the cluster.
    params = {}
    params["profile"] = profile
    params["name"] = name
    response = utils.do_request(cluster, "create", params)

    # Check that it exists.
    cluster_data = None
    try:
        cluster_data = polling_fetch(profile, name)
    except WaitTimedOut:
        msg = "Timed out waiting for '" + str(name) + "' to be created."
        raise ResourceNotCreated(msg)
    if not cluster_data:
        msg = "Cluster '" + str(name) + "' not created."
        raise ResourceNotCreated(msg)    
    
    # Send back the cluster's info.
    return cluster_data


def delete(profile, name):
    """Delete a cluster.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name of the launch configuration you want to delete.

    """
    auto_scaling_group_name = get_auto_scaling_group_name(name)
    launch_config_name = get_launch_config_name(name)

    # Make sure the cluster exists before we try to delete it.
    if not exists(profile, name):
        msg = "No cluster '" + str(name) + "'."
        raise ResourceDoesNotExist(msg)

    # If there's an auto scaling group, delete it.
    if scalinggroup_jobs.exists(profile, auto_scaling_group_name):
        scalinggroup_jobs.delete(profile, auto_scaling_group_name)
    
    # If there's a launch config, delete it.
    if launchconfig_jobs.exists(profile, launch_config_name):
        launchconfig_jobs.delete(profile, launch_config_name)

    # Now try to delete the cluster.
    params = {}
    params["profile"] = profile
    params["cluster"] = name
    response = utils.do_request(cluster, "delete", params)

    # Check that it was, in fact, deleted.
    is_deleted = polling_is_deleted(profile, name)
    cluster_data = fetch_by_name(profile, name)
    if cluster_data:
        msg = "Cluster '" + str(name) + "' was not deleted."
        raise ResourceNotDeleted(msg)


def attach_load_balancer(profile, name, load_balancer):
    """Attach a load balancer to an auto scaling group.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name of an auto scaling group.

        load_balancer
            The name of a load balancer.

    """
    # Make sure the auto scaling group exists.
    if not exists(profile, name):
        msg = "No auto scaling group '" + str(name) + "'."
        raise ResourceDoesNotExist(msg)

    # Make sure the load balancer exists.
    if not loadbalancer_jobs.exists(profile, load_balancer):
        msg = "No load balancer '" + str(load_balancer) + "'."
        raise ResourceDoesNotExist(msg)

    params = {}
    params["profile"] = profile
    params["autoscaling_group"] = name
    params["load_balancer"] = load_balancer
    utils.do_request(autoscalinggroup, "attach_load_balancer", params)


def detach_load_balancer(profile, name, load_balancer):
    """Detach a load balancer from an auto scaling group.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name of an auto scaling group.

        load_balancer
            The name of a load balancer.

    """
    # Make sure the auto scaling group exists.
    if not exists(profile, name):
        msg = "No auto scaling group '" + str(name) + "'."
        raise ResourceDoesNotExist(msg)

    # Make sure the load balancer exists.
    if not loadbalancer_jobs.exists(profile, load_balancer):
        msg = "No load balancer '" + str(load_balancer) + "'."
        raise ResourceDoesNotExist(msg)

    params = {}
    params["profile"] = profile
    params["autoscaling_group"] = name
    params["load_balancer"] = load_balancer
    utils.do_request(autoscalinggroup, "detach_load_balancer", params)