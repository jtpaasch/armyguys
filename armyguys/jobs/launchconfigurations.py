# -*- coding: utf-8 -*-

"""Jobs for launch configurations."""

from time import sleep

from botocore.exceptions import ClientError

from ..aws.autoscaling import launchconfiguration
from ..aws import profile as profile_tools

from .exceptions import ResourceAlreadyExists
from .exceptions import ResourceDoesNotExist
from .exceptions import ResourceHasDependency
from .exceptions import ResourceNotCreated
from .exceptions import ResourceNotDeleted
from .exceptions import ResourceNotReady
from .exceptions import WaitTimedOut

from . import utils

from . import instanceprofiles as instanceprofile_jobs
from . import securitygroups as sg_jobs


AMI_MAP = {
    "us-east-1": "ami-43043329",
    "us-west-1": "ami-a77b0ac7",
    "us-west-2": "ami-02a24162",
    "eu-west-1": "ami-76e95b05",
    "eu-central-1": "ami-96b6adfa",
    "ap-northeast-1": "ami-18d8de76",
    "ap-southeast-1": "ami-9f60aefc",
    "ap-southeast-2": "ami-75a38416",
}


def get_display_name(record):
    """Get the display name for a record.

    Args:

        record
            A record returned by AWS.

    Returns:
        A display name for the launch configuration.

    """
    return record["LaunchConfigurationName"]


def fetch_all(profile):
    """Fetch all launch configurations.

    Args:

        profile
            A profile to connect to AWS with.

    Returns:
        A list of launch configurations.

    """
    params = {}
    params["profile"] = profile
    response = utils.do_request(launchconfiguration, "get", params)
    data = utils.get_data("LaunchConfigurations", response)
    return data


def fetch_by_name(profile, name):
    """Fetch launch configurations by name.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name of the launch configuration you want to fetch.

    Returns:
        A list of matching launch configurations.

    """
    params = {}
    params["profile"] = profile
    params["launch_configuration"] = name
    response = utils.do_request(launchconfiguration, "get", params)
    data = utils.get_data("LaunchConfigurations", response)
    return data


def exists(profile, name):
    """Check if a launch configuration exists.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name of a launch configuration.

    Returns:
        True if it exists, False if it doesn't.

    """
    result = fetch_by_name(profile, name)
    return len(result) > 0


def polling_fetch(profile, name, max_attempts=10, wait_interval=1):
    """Try to fetch a launch configuration repeatedly until it exists.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name of a launch configuration.

        max_attempts
            The max number of times to poll AWS.

        wait_interval
            How many seconds to wait between each poll.

    Returns:
        The launch configuration's info, or None if it times out.

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
        msg = "Timed out waiting for launch configuration to be created."
        raise WaitTimedOut(msg)
    return data


def delete_error_handler(error):
    """Handle errors that arise when you delete security groups.

    Args:

        error
            An AWS ``ClientError`` exception.

    Raises:
        ``ResourceHasDependency`` if the security group is dependent
        on another resource, or ``ResourceDoseNotExist`` if the
        security group is gone.

    Returns:
        None, if the error is not worth handling.

    """
    code = error.response["Error"]["Code"]
    if code == "InvalidGroup.NotFound":
        raise ResourceDoesNotExist()
    elif code == "DependencyViolation":
        raise ResourceHasDependency()
    else:
        raise error


def create_error_handler(error):
    """Handle errors that arise when you create a cluster.

    Args:

        error
            An AWS ``ClientError`` exception.

    Raises:
        ``ResourceNotReady`` if an instance profile is not ready.

    Returns:
        None, if the error is not worth handling.

    """
    code = error.response["Error"]["Code"]
    message = error.response["Error"]["Message"]
    if message.startswith("Invalid IamInstanceProfile"):
        raise ResourceNotReady()
    else:
        raise error


def create(
        profile,
        name,
        ami=None,
        instance_type="t2.micro",
        key_pair=None,
        security_groups=None,
        public_ip=None,
        instance_profile=None,
        user_data_files=None,
        user_data=None,
        max_attempts=10,
        wait_interval=1):
    """Create a launch configuration.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name you want to give to a security group.

        ami
            The ID of an AMI to use. If none is specified,
            an ECS-optimized AMI will be used.

        instance_type
            The EC2 instance type, e.g., "m3.medium".

        key_pair
            The name of a key pair to use.

        security_groups
            A list of security group names or IDs.

        public_ip
            Assign a public IP to the EC2 instances?

        instance_profile
            The name of an instance profile for the EC2 instances.

        user_data_files
            A list of {"filepath": path, "contenttype": type} entries
            to make into a Mime Multi Part Archive for user data.

        user_data
            A list of {"contents": content, "contenttype": type} entries
            to make into a Mime Multi Part Archive for user data.

        max_attempts
            The number of times to try to create the launch configuration.

        wait_interval
            The number of seconds between each creation attempt.

    Returns:
        The security group.

    """
    # Get the AMI if needed.
    if not ami:
        region = profile_tools.get_profile_region(profile)
        if not region:
            region = "us-east-1"
        ami = AMI_MAP[region]

    # Check that the security groups exist.
    if security_groups:
        sg_ids = []
        for security_group in security_groups:
            sg_data = sg_jobs.fetch(profile, security_group)
            if not sg_data:
                msg = "No security group '" + str(security_group) + "'."
                raise ResourceDoesNotExist(msg)
            else:
                sg_id = sg_jobs.get_id(sg_data[0])
                sg_ids.append(sg_id)
        if sg_ids:
            security_groups = sg_ids

    # Check that the instance profile exists.
    if instance_profile:
        if not instanceprofile_jobs.exists(profile, instance_profile):
            msg = "No instance profile '" + str(instance_profile) + "'."
            raise ResourceDoesNotExist(msg)

    # Build the user data.
    archive = utils.create_mime_multipart_archive(user_data_files, user_data)

    # Now we can create it.
    params = {}
    params["profile"] = profile
    params["name"] = name
    params["ami"] = ami
    params["instance_type"] = instance_type
    if key_pair:
        params["key_pair"] = key_pair
    if security_groups:
        params["security_groups"] = security_groups
    if instance_profile:
        params["instance_profile"] = instance_profile
    if public_ip:
        params["public_ip"] = True
    else:
        params["public_ip"] = False
    if archive:
        params["user_data"] = archive

    # Try to create the thing. If an instance profile isn't ready,
    # we may have to wait a bit and try again.
    count = 0
    while count < max_attempts:
        response = None
        try:
            response = utils.do_request(
                launchconfiguration,
                "create",
                params,
                error_handler=create_error_handler)
        except ResourceNotReady:
            pass
        if response:
            break
        else:
            count += 1
            sleep(wait_interval)
    if not response:
        msg = "Timed out waiting for launch configuration to be created."
        raise WaitTimedOut(msg)

    # Now check that the launch configuration exists.
    launch_config_data = None
    try:
        launch_config_data = polling_fetch(profile, name)
    except WaitTimedOut:
        msg = "Timed out waiting for '" + str(name) + "' to be created."
        raise ResourceNotCreated(msg)
    if not launch_config_data:
        msg = "Launch configuration '" + str(name) + "' not created."
        raise ResourceNotCreated(msg)

    # Send back the launch configuration's info.
    return launch_config_data


def delete(profile, name):
    """Delete a launch configuration.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name of the launch configuration you want to delete.

    """
    # Make sure it exists before we try to delete it.
    launch_config = fetch_by_name(profile, name)
    if not launch_config:
        msg = "No launch configuration '" + str(name) + "'."
        raise ResourceDoesNotExist(msg)

    # Now try to delete it.
    params = {}
    params["profile"] = profile
    params["launch_configuration"] = name
    response = utils.do_request(launchconfiguration, "delete", params)

    # Check that it was, in fact, deleted.
    launch_config = fetch_by_name(profile, name)
    if launch_config:
        msg = "Launch configuration '" + str(name) + "' was not deleted."
        raise ResourceNotDeleted(msg)
