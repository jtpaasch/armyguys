# -*- coding: utf-8 -*-

"""Utilities for working with AWS auto scaling groups."""

from .. import client as boto3client


def create(
        profile,
        name,
        ami_id="ami-ddc7b6b7",
        key_pair=None,
        security_groups=None,
        instance_type="t2.micro",
        public_ip=None,
        instance_profile=None,
        user_data=None):
    """Create a launch configuration.

    Args:

        profile
            A profile to connect to AWS with.

        name
            A name to give to the launch configuration.

        ami_id
            An AMI ID to launch the EC2 instances from.
            Defaults to an ECS enabled AMI in us-east-1.
            TO DO: Get this programmatically?

        key_pair
            The name of a key pair for connecting to the EC2 instances.

        security_groups
            A list of security group IDs.

        instance_type
            The type of EC2 instance to launch.

        public_ip
            Give the EC2 instance a public IP? 

        instance_profile
            The name of an IAM instance profile to give the EC2 instance.

        user_data
            User data to add to the EC2 instance.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("autoscaling", profile)
    params = {}
    params["LaunchConfigurationName"] = name
    params["ImageId"] = ami_id
    params["InstanceType"] = instance_type
    if key_pair:
        params["KeyName"] = key_pair
    if security_groups:
        params["SecurityGroups"] = security_groups
    if public_ip:
        params["AssociatePublicIpAddress"] = True
    if instance_profile:
        params["IamInstanceProfile"] = instance_profile
    if user_data:
        params["UserData"] = user_data
    return client.create_launch_configuration(**params)


def delete(profile, launch_configuration):
    """Delete a launch configuration.

    Args:

        profile
            A profile to connect to AWS with.

        launch_configuration
            The name of the launch configuration to delete.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("autoscaling", profile)
    params = {}
    params["LaunchConfigurationName"] = launch_configuration
    return client.delete_launch_configuration(**params)


def get(profile, launch_configuration=None):
    """Get all launch configurations, or a specific one.

    Args:

        profile
            A profile to connect to AWS with.

        launch_configuration
            The name of a specific launch configuration to get.
            If omitted, all launch configurations are returned.

    Returns:
       The JSON response returned by boto3.

    """
    client = boto3client.get("autoscaling", profile)
    params = {}
    if launch_configuration:
        params["LaunchConfigurationNames"] = [launch_configuration]
    return client.describe_launch_configurations(**params)
