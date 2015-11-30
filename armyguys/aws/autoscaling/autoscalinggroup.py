# -*- coding: utf-8 -*-

"""Utilities for working with AWS auto scaling groups."""

from .. import client as boto3client


def create(
        profile,
        name,
        launch_configuration,
        subnets=None,
        availability_zones=None,
        min_size=1,
        max_size=1,
        desired_size=1):
    """Create an autoscaling group.

    Args:

        profile
            A profile to connect to AWS with.

        name
            A name to give to the autoscaling group.

        launch_configuration
            The name of the launch configuration to use.

        subnets
            A list of subnets to launch into. If you want to launch
            your cluster into a VPC, you should fill in this value
            and leave the ``availability_zones`` parameter blank.

        availability_zones
            A list of availability zones to launch into. If you do not
            want to launch your cluster into a VPC, you should fill in
            this value and leave the ``subnets`` parameter blank.

        min_size
            The min number of EC2 instances to keep in the group.

        max_size
            The max number of EC2 instances to keep in the group.

        desired_size
            The ideal number of EC2 instances to keep in the group.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("autoscaling", profile)
    params = {}
    params["AutoScalingGroupName"] = name
    params["LaunchConfigurationName"] = launch_configuration
    params["MinSize"] = min_size
    params["MaxSize"] = max_size
    params["DesiredCapacity"] = desired_size
    if subnets:
        params["VPCZoneIdentifier"] = ",".join(subnets)
    if availability_zones:
        params["AvailabilityZones"] = availability_zones
    return client.create_auto_scaling_group(**params)


def delete(profile, autoscaling_group, force=True):
    """Delete an autoscaling group.

    Args:

        profile
            A profile to connect to AWS with.

        autoscaling_group
            The name of the autoscaling group to delete.

        force
            Terminate the EC2 instances in the group?

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("autoscaling", profile)
    params = {}
    params["AutoScalingGroupName"] = autoscaling_group
    params["ForceDelete"] = force
    return client.delete_auto_scaling_group(**params)


def get(profile, autoscaling_group=None):
    """Get all autoscaling groups, or a specific one.

    Args:

        profile
            A profile to connect to AWS with.

        autoscaling_group
            The name of an autoscaling group to get.
            If omitted, all autoscaling groups are returned.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("autoscaling", profile)
    params = {}
    if autoscaling_group:
        params["AutoScalingGroupNames"] = [autoscaling_group]
    return client.describe_auto_scaling_groups(**params)


def tag(profile, autoscaling_group, key, value):
    """Add a tag to an autoscaling group.

    New instances that get launched in the group will have the tag.

    Args:

        profile
            A profile to connect to AWS with.

        autoscaling_group
            The name of the autoscaling group you want to tag.

        key
            The key/name of the tag.

        value
            The value of the tag.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("autoscaling", profile)
    tag = {
        "ResourceId": autoscaling_group,
        "ResourceType": "auto-scaling-group",
        "Key": key,
        "Value": value,
        "PropagateAtLaunch": True,
        }
    params = {}
    params["Tags"] = [tag]
    return client.create_or_update_tags(**params)
