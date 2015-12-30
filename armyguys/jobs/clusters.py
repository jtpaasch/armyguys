# -*- coding: utf-8 -*-

"""Jobs for ECS clusters."""

from base64 import b64encode
from time import sleep

import json

from botocore.exceptions import ClientError

from ..aws.iam import account
from ..aws import profile as profile_tools

from ..aws.ecs import cluster

from . import autoscalinggroups as scalinggroup_jobs
from . import availabilityzones as zone_jobs
from . import instanceprofiles as instanceprofile_jobs
from . import launchconfigurations as launchconfig_jobs
from . import loadbalancers as loadbalancer_jobs
from . import policies as policy_jobs
from . import regions as region_jobs
from . import roles as role_jobs
from . import s3buckets as s3bucket_jobs
from . import s3files as s3file_jobs

from .exceptions import ImproperlyConfigured
from .exceptions import ResourceAlreadyExists
from .exceptions import ResourceDoesNotExist
from .exceptions import ResourceHasDependency
from .exceptions import ResourceNotCreated
from .exceptions import ResourceNotDeleted
from .exceptions import ResourceNotReady
from .exceptions import WaitTimedOut

from . import utils


def get_account_id(profile):
    """Get the account ID for a profile.

    Args:

        profile
            A profile to connect to AWS with.

    Returns:
        The account ID.

    """
    params = {}
    params["profile"] = profile
    response = utils.do_request(account, "get", params)
    data = utils.get_data("User", response)
    return data['Arn'].split(':')[4]


def get_s3_bucket_name(profile):
    """Get the name of a bucket for this cluster.

    Args:

        profile
            A profile to connect to AWS with.

    Returns:
        The bucket name.

    """
    account_id = get_account_id(profile)
    region = profile_tools.get_profile_region(profile)
    bucket_name = "ecs-clusters--" + str(region) + "--" + str(account_id)
    return bucket_name


def get_ecs_config_in_s3(cluster):
    """Get the name of the ECS config file in S3.

    Args:

        cluster
            The name of the cluster it's for.

    Returns:
        The name of the file in S3, minus the bucket.

    """
    return str(cluster) + "/ecs.config"


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


def create_error_handler(error):
    """Handle errors that arise when you create a cluster.

    Args:

        error
            An AWS ``ClientError`` exception.

    Raises:
        ...

    Returns:
        None, if the error is not worth handling.

    """
    code = error.response["Error"]["Code"]
    message = error.response["Error"]["Message"]
    print(code)
    print(message)
    if message.starts_with("Invalid IamInstanceProfile"):
        raise ResourceNotReady()
    else:
        raise error
    

def create(
        profile,
        name,
        instance_profile,
        instance_type=None,
        key_pair=None,
        security_groups=None,
        user_data_files=None,
        user_data=None,
        min_size=None,
        max_size=None,
        desired_size=None,
        availability_zones=None,
        subnets=None,
        vpc=None,
        tags=None,
        dockerhub_email=None,
        dockerhub_username=None,
        dockerhub_password=None):
    """Create an ECS cluster.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name you want to give to the cluster.

        instance_profile
            The name of an ECS intsance profile.

        key_pair
            The name of a key pair to use.

        security_groups
            A list of security group names or IDs.

        user_data_files
            A list of {"filepath": path, "contenttype": type} entries
            to make into a Mime Multi Part Archive for user data.

        user_data
            A list of {"contents": contents, "contenttype": type} entries
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

        dockerhub_email
            An email address for a Docker Hub account.

        dockerhub_username
            A username for a Docker Hub account.

        dockerhub_password
            A password for a Docker Hub account.

    Returns:
        The cluster's info.

    """
    auto_scaling_group_name = get_auto_scaling_group_name(name)
    launch_config_name = get_launch_config_name(name)
    s3_bucket_name = get_s3_bucket_name(profile)
    ecs_config_in_s3 = get_ecs_config_in_s3(name)

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

    # We need all Docker Hub credentials, if any.
    dockerhub_credentials = [
        dockerhub_email,
        dockerhub_username,
        dockerhub_password]
    if any(dockerhub_credentials) and not all(dockerhub_credentials):
        msg = "Docker Hub requires an email, username, and password."
        raise ImproperlyConfigured(msg)

    # Construct the authentication information.
    auth_data = None
    if all(dockerhub_credentials):
        auth_data = '{"https://index.docker.io/v1/":{' \
                    + '"username":"' \
                    + str(dockerhub_username) \
                    + '","password":"' \
                    + str(dockerhub_password) \
                    + '","email":"' \
                    + str(dockerhub_email) \
                    + '"}}'

    # Construct the ecs.config file.
    ecs_config = "ECS_CLUSTER=" + str(name) + "\n"
    if auth_data:
        ecs_config += "ECS_ENGINE_AUTH_TYPE=docker\n"
        ecs_config += "ECS_ENGINE_AUTH_DATA=" + str(auth_data) + "\n"

    # Construct a script that downloads it.
    ecs_config_download_script = "#!/bin/bash\n" \
                                 + "yum install -y aws-cli\n" \
                                 + "aws s3 cp s3://" \
                                 + s3_bucket_name \
                                 + "/" + ecs_config_in_s3 \
                                 + " /etc/ecs/ecs.config\n"

    # Add that script to the user data.
    if not user_data:
        user_data = []
    user_data.append({
        "contenttype": "text/x-shellscript",
        "contents": ecs_config_download_script
        })

    # Create an S3 bucket for this cluster, if it doesn't already exist.
    if not s3bucket_jobs.exists(profile, s3_bucket_name):
        s3bucket_jobs.create(profile, s3_bucket_name, private=True)

    # Upload the ecs.config file to S3.
    s3file_jobs.create(
        profile,
        bucket=s3_bucket_name,
        name=ecs_config_in_s3,
        contents=ecs_config)

    # Create an instance profile, if one hasn't been specified.
    if not instance_profile:
        instance_profile_data = create_instance_profile(profile, name)

        # Get its name.
        if not instance_profile_data:
            msg = "Instance profile not created."
            raise RseourceNotCreated(msg)
        else:
            instance_profile = utils.get_data(
                "InstanceProfileName",
                instance_profile_data[0])

    # We need an instance profile.
    if not instance_profile:
        msg = "No instance profile."
        raise ImproperlyConfigured(msg)

    # Add a tag indicating which cluster this all belongs to.
    if not tags:
        tags = []
    tags.append({"Key": "ECS Cluster", "Value": name})

    # Create the launch configuration.
    params = {}
    params["profile"] = profile
    params["name"] = launch_config_name
    if instance_type:
        params["instance_type"] = instance_type
    params["key_pair"] = key_pair
    params["instance_profile"] = instance_profile
    params["user_data_files"] = user_data_files
    params["user_data"] = user_data
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
    s3_bucket_name = get_s3_bucket_name(profile)
    ecs_config_in_s3 = get_ecs_config_in_s3(name)

    # Make sure the cluster exists before we try to delete it.
    if not exists(profile, name):
        msg = "No cluster '" + str(name) + "'."
        raise ResourceDoesNotExist(msg)

    # If there's an ECS config file in S3, delete it.
    if s3file_jobs.exists(profile, s3_bucket_name, ecs_config_in_s3):
        s3file_jobs.delete(profile, s3_bucket_name, ecs_config_in_s3)
    
    # If there's an auto scaling group, delete it.
    if scalinggroup_jobs.exists(profile, auto_scaling_group_name):
        scalinggroup_jobs.delete(profile, auto_scaling_group_name)
    
    # If there's a launch config, delete it.
    if launchconfig_jobs.exists(profile, launch_config_name):
        launchconfig_jobs.delete(profile, launch_config_name)

    # If there's an instance profile, delete it.
    delete_instance_profile(profile, name)

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


def attach_load_balancer(profile, cluster, load_balancer):
    """Attach a load balancer to a cluster's auto scaling group.

    Args:

        profile
            A profile to connect to AWS with.

        cluster
            The name of a cluster.

        load_balancer
            The name of a load balancer.

    """
    auto_scaling_group_name = get_auto_scaling_group_name(cluster)

    # Make sure the auto scaling group exists.
    if not exists(profile, auto_scaling_group_name):
        msg = "No auto scaling group '" + str(auto_scaling_group_name) + "'."
        raise ResourceDoesNotExist(msg)

    # Make sure the load balancer exists.
    if not loadbalancer_jobs.exists(profile, load_balancer):
        msg = "No load balancer '" + str(load_balancer) + "'."
        raise ResourceDoesNotExist(msg)

    params = {}
    params["profile"] = profile
    params["autoscaling_group"] = auto_scaling_group_name
    params["load_balancer"] = load_balancer
    utils.do_request(autoscalinggroup, "attach_load_balancer", params)


def detach_load_balancer(profile, cluster, load_balancer):
    """Detach a load balancer from a cluster's auto scaling group.

    Args:

        profile
            A profile to connect to AWS with.

        cluster
            The name of a cluster.

        load_balancer
            The name of a load balancer.

    """
    auto_scaling_group_name = get_auto_scaling_group_name(cluster)

    # Make sure the auto scaling group exists.
    if not exists(profile, name):
        msg = "No auto scaling group '" + str(auto_scaling_group_name) + "'."
        raise ResourceDoesNotExist(msg)

    # Make sure the load balancer exists.
    if not loadbalancer_jobs.exists(profile, load_balancer):
        msg = "No load balancer '" + str(load_balancer) + "'."
        raise ResourceDoesNotExist(msg)

    params = {}
    params["profile"] = profile
    params["autoscaling_group"] = auto_scaling_group_name
    params["load_balancer"] = load_balancer
    utils.do_request(autoscalinggroup, "detach_load_balancer", params)


def create_instance_profile(profile, cluster):
    """Create an instance profile for the cluster.

    Args:

        profile
            A profile to connect to AWS with.

        cluster
            The name of a cluster.

    """
    role_name = str(cluster) + "--ecs-role"
    policy_name = str(cluster) + "--ecs-policy"
    instance_profile_name = str(cluster) + "--ecs-instance-profile"

    # Create a role that EC2 instances can assume:
    contents = {
        "Version": "2012-10-17",
        "Statement": {
            "Effect": "Allow",
            "Principal": {
                "Service": "ec2.amazonaws.com",
            },
            "Action": "sts:AssumeRole",
        }
    }
    role_jobs.create(profile, role_name, contents=contents)

    # Create a policy that lets the ECS agent do what it needs.
    contents = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "ec2:Describe*",
                    "elasticloadbalancing:*",
                    "ecs:*",
                    "iam:ListInstanceProfiles",
                    "iam:ListRoles",
                    "iam:PassRole"
                ],
                "Resource": "*"
            }
        ]
    }
    policy_jobs.create(profile, policy_name, contents=contents)

    # Attach the policy to the role.
    role_jobs.attach(profile, role_name, policy_name)

    # Create an instance profile.
    instanceprofile_jobs.create(profile, instance_profile_name)

    # Attach the role to the instance profile.
    instanceprofile_jobs.attach(profile, instance_profile_name, role_name)

    # Return the instance profile.
    return instanceprofile_jobs.fetch_by_name(
        profile,
        instance_profile_name)


def delete_instance_profile(profile, cluster):
    """Create an instance profile for the cluster.

    Args:

        profile
            A profile to connect to AWS with.

        cluster
            The name of a cluster.

    """
    role_name = str(cluster) + "--ecs-role"
    policy_name = str(cluster) + "--ecs-policy"
    instance_profile_name = str(cluster) + "--ecs-instance-profile"

    # Do these resources exist?
    is_role = role_jobs.exists(profile, role_name)
    is_policy = policy_jobs.exists(profile, policy_name)
    is_instance_profile = instanceprofile_jobs.exists(
        profile,
        instance_profile_name)

    # Detach the role from the instance profile if needed.
    if is_role and is_instance_profile:

        # Is the role attached?
        is_role_attached = instanceprofile_jobs.is_attached(
            profile,
            instance_profile_name,
            role_name)

        # Detach it.
        if is_role_attached:
            instanceprofile_jobs.detach(profile, instance_profile_name, role_name)

        # Make sure it got detached.
        is_role_detached = instanceprofile_jobs.is_detached(
            profile,
            instance_profile_name,
            role_name)
        if not is_role_detached:
            msg = "Could not detach '" + str(role_name) \
                  + "' from '" + str(instance_profile_name) + "'."
            raise ResourceNotDetached(msg)

    # Delete the instance profile, if needed.
    if is_instance_profile:
        instanceprofile_jobs.delete(profile, instance_profile_name)

        # Make sure it got deleted.
        if instanceprofile_jobs.exists(profile, instance_profile_name):
            msg = "Instance profile '" + str(instance_profile_name) \
                  + "' not deleted."
            raise ResourceNotDeleted(msg)

    # Detach the policy from the role if needed.
    if is_role and is_policy:
        role_jobs.detach(profile, role_name, policy_name)

    # Delete the role, if needed.
    if is_role:
        role_jobs.delete(profile, role_name)

        # Make sure it got deleted.
        if role_jobs.exists(profile, role_name):
            msg = "Role '" + str(role_name) + "' not deleted."
            raise ResourceNotDeleted(msg)

    # Delete the policy, if needed.
    if is_policy:
        policy_jobs.delete(profile, policy_name)

        # Make sure it got deleted.
        if policy_jobs.exists(profile, policy_name):
            msg = "Policy '" + str(policy_name) + "' not deleted."
            raise ResourceNotDeleted(msg)
