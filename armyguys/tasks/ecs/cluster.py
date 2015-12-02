# -*- coding: utf-8 -*-

"""For creating and managing ECS clusters."""

from base64 import b64encode

from polarexpress.aws.autoscaling import autoscalinggroup
from polarexpress.aws.autoscaling import launchconfiguration
from polarexpress.aws.ecs import cluster
from polarexpress.aws.ecs import containerinstance
from polarexpress.aws.ecs import service

from polarexpress.aws import ec2
from polarexpress.aws import profile
from polarexpress.aws import s3
from polarexpress.aws import securitygroup
from polarexpress.aws import subnet

from polarexpress.tasks import utils


ECS_CONFIG_FILE_ON_INSTANCE = "/etc/ecs/ecs.config"


def get_launchconfig_name(cluster_name):
    """Get the name for a cluster's launch config.

    Args:

        cluster_name
            The name of the cluster.

    Returns:
        The cluster's launch config name (a string).

    """
    return cluster_name + "--launchconfig"


def get_autoscalinggroup_name(cluster_name):
    """Get the name for a cluster's auto scaling group.

    Args:

        cluster_name
            The name of the cluster.

    Returns:
        The cluster's auto scaling group name (a string).

    """
    return cluster_name + "--autoscaling-group"


def get_securitygroup_name(cluster_name):
    """Get the name for a cluster's security group.

    Args:

        cluster_name
            The name of the cluster.

    Returns:
        The cluster's security group name (a string).

    """
    return cluster_name + "--security-group"


def create_ecs_auth_data(
        dockerhub_email,
        dockerhub_username,
        dockerhub_password):
    """Create ECS auth data for a Docker Hub account.

    Args:

        dockerhub_email
            An email address associated with a Docker Hub account.

        dockerhub_username
            A username associated with a Docker Hub account.

        dockerhub_password
            A password associated with a Docker Hub account.

    Returns:
        A JSON string with Docker Hub auth data.

    """
    utils.heading("Creating ECS AUTH data")
    original_auth_string = dockerhub_username + ":" + dockerhub_password
    utf8_encoded_original_auth_string = original_auth_string.encode("utf-8")
    b64encoded_auth_string = b64encode(utf8_encoded_original_auth_string)
    final_auth_string = b64encoded_auth_string.decode("utf-8")
    auth_data = '{"https://index.docker.io/v1/": {' \
                + '"auth": "' + final_auth_string + '",' \
                + '"email": "' + dockerhub_email + '"' \
                + '}}'
    utils.emphasize("AUTH DATA:")
    utils.echo(auth_data)
    return auth_data


def create_ecs_config_file_contents(
        ecs_auth_type,
        ecs_auth_data,
        cluster):
    """Create an ECS config file to go at /etc/ecs/ecs.config.

    Args:

        ecs_auth_type
            The value to give to ECS_ENGINE_AUTH_TYPE. Likely "dockercfg".

        ecs_auth_data
            The value to give to ECS_ENGINE_AUTH_DATA. Likely a dockercfg
            styled JSON string like found in /root/.docker/config.json.

        cluster
            The name of a cluster to give to the ECS_CLUSTER setting.

    Returns:
        The contents (as a string) of an ECS config file for AWS.

    """
    utils.heading("Generating ecs.config file contents")
    contents = "ECS_ENGINE_AUTH_TYPE=" + ecs_auth_type + "\n" \
               + "ECS_ENGINE_AUTH_DATA=" + ecs_auth_data + "\n" \
               + "ECS_CLUSTER=" + cluster
    utils.emphasize("ECS CONFIG FILE CONTENTS:")
    utils.echo(contents)
    return contents


def upload_file_to_s3(
        aws_profile,
        s3bucket,
        s3key,
        contents):
    """Upload some contents to S3.

    Args:

        aws_profile
            A profile to connect to AWS with.

        s3bucket
            The name of a bucket to put the file in.
            The bucket will be created if it doesn't exist.

        s3key
            The key of the file, e.g., "myfolder/myfile.cfg".

        contents
            The (string) contents to put in the file.

    """
    utils.heading("Creating S3 bucket (if it doesn't exist)")
    response = s3.bucket.create(
        profile=aws_profile,
        name=s3bucket,
        private=True)
    utils.echo_data(response)

    utils.heading("Uploading file contents")
    response = s3.file.create(
        profile=aws_profile,
        s3bucket=s3bucket,
        s3key=s3key,
        contents=contents)
    utils.echo_data(response)


def get_cluster_info(aws_profile, cluster_name):
    """Get info about a cluster.

    Args:

        aws_profile
            A profile to connect to AWS with.

        cluster_name
            The name of the cluster to fetch info about.

    Returns:
        The JSON response returned by boto3.

    """
    response = cluster.get(aws_profile, cluster=cluster_name)
    clusters = response["clusters"]
    result = []
    if clusters:
        result = [x for x in clusters
                  if x["clusterName"] == cluster_name
                  and x["status"] == "ACTIVE"]
    return result


def get_launchconfig_info(aws_profile, launchconfig_name):
    """Get info about a launch configuration.

    Args:

        aws_profile
            A profile to connect to AWS with.

        launchconfig_name
            The name of the launch config to fetch info about.

    Returns:
        The JSON response returned by boto3.

    """
    response = launchconfiguration.get(aws_profile, launchconfig_name)
    launch_configs = response["LaunchConfigurations"]
    result = []
    if launch_configs:
        result = [x for x in launch_configs
                  if x["LaunchConfigurationName"] == launchconfig_name]
    return result


def get_securitygroup_info(aws_profile, securitygroup_name):
    """Get info about a security group.

    Args:

        aws_profile
            A profile to connect to AWS with.

        securitygroup_name
            The name of the security group to fetch info about.

    Returns:
        The JSON response returned by boto3.

    """
    response = securitygroup.get(aws_profile, securitygroup_name)
    security_groups = response["SecurityGroups"]
    result = []
    if security_groups:
        result = [x for x in security_groups
                  if x["GroupName"] == securitygroup_name]
    return result


def get_autoscalinggroup_info(aws_profile, autoscalinggroup_name):
    """Get info about an autoscaling group.

    Args:

        aws_profile
            A profile to connect to AWS with.

        autoscalinggroup_name
            The name of the autoscaling group to fetch info about.

    Returns:
        The JSON response returned by boto3.

    """
    response = autoscalinggroup.get(aws_profile, autoscalinggroup_name)
    as_groups = response["AutoScalingGroups"]
    result = []
    if as_groups:
        result = [x for x in as_groups
                  if x["AutoScalingGroupName"] == autoscalinggroup_name]
    return result


def get_containerinstances_info(aws_profile, cluster_name):
    """Get info about container instances in a cluster.

    Args:

        aws_profile
            A profile to connect to AWS with.

        cluster_name
            The name of the cluster.

    Returns:
        The JSON response returned by boto3.

    """
    response = containerinstance.get(aws_profile, cluster=cluster_name)
    instances = []
    if response:
        instances = response.get("containerInstances")
    result = []
    if instances:
        result = instances
    return result


def create_cluster(
        aws_profile,
        cluster_name,
        instance_type,
        instance_profile_name,
        key_pair=None,
        vpc_id=None,
        availability_zones=None,
        security_groups=None,
        ecs_config_file_in_s3=None):
    """Create an ECS cluster.

    Args:

        aws_profile
            A profile to connect to AWS with.

        cluster_name
            A name to give to the cluster.

        instance_type
            An EC2 instance type to run the cluster on, e.g., "t2.micro".

        instance_profile_name
            The name of an ECS-enabled instance profile to give
            to the EC2 instances. This profile MUST have ECS permissions.

        key_pair
            The name of a key pair to give to the cluster's EC2 instances.

        vpc_id
            The ID of a VPC to launch the cluster in. If you are not
            launching into a cluster, you should leave this field blank
            and fill in the ``availability_zones`` parameter instead.

        availability_zones
            A list of availability zones to launch into. If you are
            launching into a VPC, you should leave this field blank
            and fill in the ``vpc_id`` parameter instead.

        security_groups
            A list of security groups to launch the cluster in.
            If you are launching your cluster into a VPC, these must
            be group IDs. Otherwise, they can be group names.

        ecs_config_file_in_s3
            The full bucket/key path to an ECS config file in S3.
            If you provide a value here, the EC2 instances will download
            the file and store it as /etc/ecs/ecs.config.
            This is the file the ECS agent reads when it starts up. Any
            ECS configuration should go in this file.

    """
    launchconfig_name = get_launchconfig_name(cluster_name)
    autoscalinggroup_name = get_autoscalinggroup_name(cluster_name)
    securitygroup_name = get_securitygroup_name(cluster_name)

    # Make sure we have a VPC ID or availability zones.
    utils.heading("Checking VPC or availability zones")
    if vpc_id and availability_zones:
        utils.error("Specify either: ``vpc_id``, or ``availability_zones``.")
        utils.exit()
    if availability_zones:
        utils.emphasize("AVAILABILITY ZONES: " + str(availability_zones))
    elif vpc_id:
        utils.emphasize("VPC ID: " + str(vpc_id))

    # Check that the cluster doesn't already exist.
    utils.heading("Checking that the cluster doesn't already exist.")
    cluster_info = get_cluster_info(aws_profile, cluster_name)
    utils.echo_data(cluster_info)
    if cluster_info:
        utils.error("Cluster '" + cluster_name + "' already exists.")
        utils.exit()
    else:
        msg = "OK. No cluster already named '" + cluster_name + "'."
        utils.emphasize(msg)

    # Make sure the launch configuration doesn't already exist.
    utils.heading("Checking that a launch config doesn't already exist.")
    launchconfig_info = get_launchconfig_info(aws_profile, launchconfig_name)
    utils.echo_data(launchconfig_info)
    if launchconfig_info:
        msg = "Launch config '" + launchconfig_name + "' already exists."
        utils.error(msg)
        utils.exit()
    else:
        msg = "OK. No launch config '" + launchconfig_name + "'."
        utils.emphasize(msg)

    # Make sure the security group doesn't already exist.
    utils.heading("Checking that a security group doesn't already exist.")
    sg_info = get_securitygroup_info(aws_profile, securitygroup_name)
    utils.echo_data(sg_info)
    if sg_info:
        msg = "Security group '" + securitygroup_name + "' already exists."
        utils.error(msg)
        utils.exit()
    else:
        msg = "OK. No security group '" + securitygroup_name + "'."
        utils.emphasize(msg)

    # Make sure the autoscaling group doesn't exist.
    utils.heading("Checking that an autoscaling group doesn't already exist.")
    asg_info = get_autoscalinggroup_info(aws_profile, autoscalinggroup_name)
    utils.echo_data(asg_info)
    if asg_info:
        msg = "Auto scaling group '" \
              + autoscalinggroup_name \
              + "' already exists."
        utils.error(msg)
        utils.exit()
    else:
        msg = "OK. No auto scaling group '" + autoscalinggroup_name + "'."
        utils.emphasize(msg)

    # Generate the user data.
    utils.heading("Generating user data field")
    user_data = "#!/bin/bash\n" \
                + "yum install -y aws-cli\n" \
                + "aws s3 cp s3://" + str(ecs_config_file_in_s3) \
                + " " \
                + ECS_CONFIG_FILE_ON_INSTANCE \
                + "\n\n"
    utils.echo_data(user_data)

    # Create a security group for this cluster.
    utils.heading("Creating security group")
    params = {}
    params["profile"] = aws_profile
    params["name"] = securitygroup_name
    if vpc_id:
        params["vpc"] = vpc_id
    response = securitygroup.create(**params)
    utils.echo_data(response)
    securitygroup_id = response["GroupId"]
    utils.emphasize("GROUP ID: " + str(securitygroup_id))

    # Tag the security group.
    utils.heading("Tagging security group")
    response = securitygroup.tag(
        profile=aws_profile,
        security_group=securitygroup_id,
        key="ECS Cluster",
        value=cluster_name)
    utils.echo_data(response)
    utils.emphasize("TAG NAME: ECS Cluster")
    utils.emphasize("TAG VALUE: " + str(cluster_name))

    # Add the security group to the list.
    if security_groups:
        security_groups.append(securitygroup_id)
    else:
        security_groups = [securitygroup_id]

    # Create a cluster.
    utils.heading("Creating cluster")
    response = cluster.create(
        profile=aws_profile,
        name=cluster_name)
    utils.echo_data(response)

    # Create a launch config.
    utils.heading("Creating launch configuration")
    params = {}
    params["profile"] = aws_profile
    params["name"] = launchconfig_name
    params["instance_profile"] = instance_profile_name
    params["instance_type"] = instance_type
    params["user_data"] = user_data
    if key_pair:
        params["key_pair"] = key_pair
    if security_groups:
        params["security_groups"] = security_groups
    if vpc_id:
        params["public_ip"] = True  # Allowed to be True only in VPCs.
    else:
        params["public_ip"] = False
    response = launchconfiguration.create(**params)
    utils.echo_data(params)
    utils.echo_data(response)

    # Get subnets in the VPC, if we're launching into a VPC.
    utils.heading("Getting subnets in VPC")
    subnet_ids = None
    if not vpc_id:
        utils.echo("Not launching into a VPC. Subnets n/a.")
    else:
        response = subnet.get(profile=aws_profile)
        subnets = response["Subnets"]
        utils.echo_data(subnets)
        subnet_ids = [x["SubnetId"] for x in subnets if x["VpcId"] == vpc_id]
        utils.emphasize("SUBNET IDS: " + str(subnet_ids))

    # Launch the auto scaling group.
    utils.heading("Creating auto scaling group")
    params = {}
    params["profile"] = aws_profile
    params["name"] = autoscalinggroup_name
    params["launch_configuration"] = launchconfig_name
    if subnet_ids:
        params["subnets"] = subnet_ids
    if availability_zones:
        params["availability_zones"] = availability_zones
    response = autoscalinggroup.create(**params)
    utils.echo_data(params)
    utils.echo_data(response)

    # Tag the auto scaling group.
    utils.heading("Tagging auto scaling group")
    response = autoscalinggroup.tag(
        profile=aws_profile,
        autoscaling_group=autoscalinggroup_name,
        key="ECS Cluster",
        value=cluster_name)
    utils.echo_data(response)
    utils.emphasize("TAG NAME: ECS Cluster")
    utils.emphasize("TAG VALUE: " + str(cluster_name))

    # Add the ECS config as a tag to the auto scaling group.
    utils.heading("Tagging auto scaling group")
    response = autoscalinggroup.tag(
        profile=aws_profile,
        autoscaling_group=autoscalinggroup_name,
        key=ECS_CONFIG_FILE_ON_INSTANCE,
        value=ecs_config_file_in_s3)
    utils.echo_data(response)
    utils.emphasize("TAG NAME: " + str(ECS_CONFIG_FILE_ON_INSTANCE))
    utils.emphasize("TAG VALUE: " + str(ecs_config_file_in_s3))

    # Exit nicely.
    utils.echo("")
    utils.echo("Done.")


def delete_cluster(aws_profile, cluster_name):
    """Delete an ECS cluster and the resources it runs on.

    Args:

        aws_profile
            A profile to connect to AWS with.

        cluster_name
            The name of the cluster you want to delete.

    """
    launchconfig_name = get_launchconfig_name(cluster_name)
    autoscalinggroup_name = get_autoscalinggroup_name(cluster_name)
    securitygroup_name = get_securitygroup_name(cluster_name)

    has_cluster = False
    has_security_group = False
    has_autoscaling_group = False
    has_launchconfig = False

    # Get info about the cluster.
    utils.heading("Getting info about cluster")
    cluster_info = get_cluster_info(aws_profile, cluster_name)
    if cluster_info:
        utils.echo_data(cluster_info)
        has_cluster = True
        msg = "OK. Cluster '" + cluster_name + "' found."
        utils.echo(msg)
    else:
        msg = "No cluster '" + cluster_name + "'."
        utils.error(msg)
    
    # Get all container instances in the cluster.
    utils.heading("Getting container instances")
    instance_ids = []
    if not has_cluster:
        utils.error("No cluster found. Getting instances n/a.")
    else:
        container_instances = get_containerinstances_info(
            aws_profile,
            cluster_name)
        if container_instances:
            instance_ids = [x["ec2InstanceId"] for x in container_instances]
            utils.emphasize("INSTANCE IDS:")
            utils.echo_data(instance_ids)
        else:
            utils.echo("No container instances.")

    # Make sure the security group exists (before we try to delete it).
    utils.heading("Checking that the security group exists.")
    sg_info = get_securitygroup_info(aws_profile, securitygroup_name)
    if sg_info:
        utils.echo_data(sg_info)
        sg_id = sg_info[0]["GroupId"]
        has_security_group = True
        msg = "OK. Security group '" + securitygroup_name + "' exists."
        utils.emphasize(msg)
    else:
        msg = "No security group '" + securitygroup_name + "'."
        utils.error(msg)

    # Make sure the launch config exists (before we try to delete it).
    utils.heading("Checking that the launch config exists.")
    launchconfig_info = get_launchconfig_info(aws_profile, launchconfig_name)
    if launchconfig_info:
        utils.echo_data(launchconfig_info)
        has_launchconfig = True
        msg = "OK. Launch configuration '" + launchconfig_name + "' exists."
        utils.emphasize(msg)
    else:
        msg = "No launch configuration '" + launchconfig_name + "'."
        utils.error(msg)

    # Get info about the autoscaling group.
    asg_info = get_autoscalinggroup_info(aws_profile, autoscalinggroup_name)

    # Make sure the auto scaling group exists (before we try to delete it).
    utils.heading("Checking that the auto scaling group exists.")
    if asg_info:
        utils.echo_data(asg_info)
        has_autoscaling_group = True
        msg = "OK. Auto scaling group '" + autoscalinggroup_name + "' exists."
        utils.emphasize(msg)
    else:
        msg = "No auto scaling group '" + securitygroup_name + "'."
        utils.error(msg)

    # Find the ECS config file in S3, if it's noted in the
    # auto scaling group's tags.
    utils.heading("Checking for ECS config file in auto scaling group tags")
    ecs_config_file_in_s3 = None
    if not asg_info:
        utils.echo("No ECS config in tags.")
    else:
        asg_tags = asg_info[0]["Tags"]
        utils.echo_data(asg_tags)
        for tag in asg_tags:
            if tag.get("Key") == ECS_CONFIG_FILE_ON_INSTANCE:
                ecs_config_file_in_s3 = tag.get("Value")
                utils.emphasize("ECS config file in s3:")
                utils.echo(ecs_config_file_in_s3)
                break
        if not ecs_config_file_in_s3:
            utils.echo("No ECS config in tags.")

    # Delete the ECS config file from S3.
    utils.heading("Deleting ECS config file from S3")
    if not ecs_config_file_in_s3:
        utils.error("No ECS config file. Deleting n/a.")
    else:
        s3_path_parts = ecs_config_file_in_s3.split("/", 1)
        if len(s3_path_parts) == 2:
            s3bucket = s3_path_parts[0]
            s3key = s3_path_parts[1]
            utils.echo("S3 Bucket: " + str(s3bucket))
            utils.echo("S3 Key: " + str(s3key))
            response = s3.file.delete(aws_profile, s3key, s3bucket)
            utils.echo_data(response)
        else:
            msg = "Can't parse '" + ecs_config_file_in_s3 + "'."
            utils.error(msg)
            utils.exit()

    # Delete the autoscaling group.
    utils.heading("Deleting auto scaling group")
    if not has_autoscaling_group:
        utils.error("No auto scaling group detected. Deleting n/a.")
    else:
        response = autoscalinggroup.delete(
            profile=aws_profile,
            autoscaling_group=autoscalinggroup_name)
        utils.echo_data(response)

    # Wait until the instances terminate.
    utils.heading("Waiting for instances to terminate")
    if instance_ids:
        utils.echo("Terminating:")
        utils.echo_data(instance_ids)
        response = ec2.wait_for_instances_to_terminate(
            profile=aws_profile,
            instances=instance_ids)
        utils.echo_data(response)
    else:
        utils.error("No instances. Waiting n/a.")

    # Delete the launch config.
    utils.heading("Deleting launch configuration")
    if not has_launchconfig:
        utils.error("No launch configuration detected. Deleting n/a.")
    else:
        response = launchconfiguration.delete(
            profile=aws_profile,
            launch_configuration=launchconfig_name)
        utils.echo_data(response)

    # Delete the security group.
    utils.heading("Deleting the security group")
    if not has_security_group:
        utils.error("No security group detected. Deleting n/a.")
    else:
        response = securitygroup.delete(
            profile=aws_profile,
            group_id=sg_id)
        utils.echo_data(response)

    # Delete any services.
    utils.heading("Stopping services")
    response = service.get(aws_profile, cluster=cluster_name)
    if not response:
        utils.echo("No services to stop.")
    else:
        utils.echo_data(response)
        services = response.get("services")
        for ecs_service in services:
            service_name = ecs_service["serviceName"]
            response = service.update(
                profile=aws_profile,
                cluster=cluster_name,
                service=service_name,
                count=0)
            utils.echo("Stopping " + str(service_name))
            response = service.delete(
                profile=aws_profile,
                cluster=cluster_name,
                service=service_name)
            utils.echo("Deleting " + str(service_name))

    # Delete the cluster.
    utils.heading("Deleting cluster")
    if not has_cluster:
        utils.error("No cluster detected. Deleting n/a.")
    else:
        response = cluster.delete(profile=aws_profile, cluster=cluster_name)
        utils.echo_data(response)

    # Exit nicely.
    utils.echo("")
    utils.echo("Done.")


if __name__ == "__main__":
    # Get an AWS profile.
    profile_name = "default"
    aws_profile = profile.configured(profile_name)

    # Set some parameters.
    cluster_name="joe-cluster"
    instance_type="t2.micro"
    instance_profile_name="ecs-instance-profile"
    key_pair = "quickly_fitchet"
    vpc_id = "vpc-8c65bce8"  # None
    availability_zones = None  # ["us-east-1c", "us-east-1e"]
    security_groups = None  # ["sg-dd5d23bb"]

    # Delete the cluster.
    delete_cluster(aws_profile=aws_profile, cluster_name=cluster_name)
    utils.exit()
    
    # Params for dockerhub/ecs.config.
    region = aws_profile._session._profile_map[profile_name]["region"]
    dockerhub_username="mechanicalautomaton",
    s3bucket = "jtpaasch-" + region
    s3key = "ecs/clusters/" + cluster_name + "/ecs.config"
    full_s3_address = s3bucket + "/" + s3key
    
    # Create an ecs.config file.
    auth_data = create_ecs_auth_data(
        dockerhub_email="mechanical.automaton@gmail.com",
        dockerhub_username="mechanicalautomaton",
        dockerhub_password="Dp#6B7quM6nepMXvp4qdJv%V")
    ecs_config_file_contents = create_ecs_config_file_contents(
        ecs_auth_type="dockercfg",
        ecs_auth_data=auth_data,
        cluster=cluster_name)
    upload_file_to_s3(
        aws_profile=aws_profile,
        s3bucket=s3bucket,
        s3key=s3key,
        contents=ecs_config_file_contents)

    # Create the cluster.
    create_cluster(
        aws_profile=aws_profile,
        cluster_name=cluster_name,
        instance_type=instance_type,
        instance_profile_name=instance_profile_name,
        key_pair=key_pair,
        vpc_id=vpc_id,
        availability_zones=availability_zones,
        security_groups=security_groups,
        ecs_config_file_in_s3=full_s3_address)
