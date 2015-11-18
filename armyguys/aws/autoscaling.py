# -*- coding: utf-8 -*-

"""Utilities for working with AWS auto scaling groups."""

from . import client as boto3client


def create_launch_configuration(profile,
                                name,
                                ami_id="ami-ddc7b6b7",
                                key_pair=None,
                                security_groups=None,
                                instance_type="t2.micro",
                                public_ip=True,
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
            Give the EC2 instance a public IP? Defaults to ``True``
            because ECS clusters won't work without that.

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


def delete_launch_configuration(profile, name):
    """Delete a launch configuration.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name of the launch configuration to delete.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("autoscaling", profile)
    params = {}
    params["LaunchConfigurationName"] = name
    return client.delete_launch_configuration(**params)


def create_autoscaling_group(profile,
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


def delete_autoscaling_group(profile, name, force=True):
    """Delete an autoscaling group.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name of the autoscaling group to delete.

        force
            Terminate the EC2 instances in the group?

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("autoscaling", profile)
    params = {}
    params["AutoScalingGroupName"] = name
    params["ForceDelete"] = force
    return client.delete_auto_scaling_group(**params)
