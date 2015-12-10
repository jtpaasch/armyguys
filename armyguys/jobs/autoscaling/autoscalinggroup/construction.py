# -*- coding: utf-8 -*-

"""Jobs for creating auto scaling groups."""

from ....aws import profile as profile_tools
from ....aws.autoscaling import launchconfiguration

from ...exceptions import BadResponse
from ...exceptions import ResourceAlreadyExists
from ...exceptions import TooManyRecords

from . import fetch


def create(
        profile,
        name,
        instance_type,
        vpc=None,
        instance_profile=None,
        security_groups=None,
        key_pair=None,
        user_data=None,
        public_ip=None,
        reports=None,
        aws_reporter=None,
        job_heading_reporter=None,
        job_data_reporter=None,
        job_text_reporter=None,
        job_warning_reporter=None,
        job_error_reporter=None,
        stdout_reporter=None,
        stderr_reporter=None):
    """Create a launch configuration.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name you want to give to the security group.

        instance_type
            An EC2 instance type, e.g., "m3.medium" or "t2.micro".
            Note that not all instance types work: m1 doesn't work
            with ECS, and t2.micro only works inside a VPC, for example.

        vpc
            The ID of a VPC you want to create the group in.

        instance_profile
            An ECS-enabled instance profile.

        security_groups
            A list of security group IDs.

        key_pair
            A key pair for the EC2 instances.

        user_data
            An init script for the EC2 instances.

        public_ip
            Assign a public IP to the instances?
            Should be ``True`` only inside a VPC.

        reports
            A list of reports to send info to.

        aws_reporter
            AWS responses will be sent to this reporter.

        job_data_reporter
            Job data structures will be sent to this reporter.

        job_text_reporter
            Simple text strings from jobs will be sent to this reporter.

        job_warning_reporter
            Job warnings will be sent to this reporter.

        job_error_reporter
            Job errors will be sent to this reporter.

        stdout_reporter
            Info meant for STDOUT will be sent to this reporter.

        stderr_reporter
            Info meant for STDERR will be sent to this reporter.

    Return:
        The data returned by AWS, or None if none were found.

    """
    if job_heading_reporter:
        job_heading_reporter(reports, "Creating launch configuration")
    params = {}
    params["profile"] = profile
    params["name"] = name
    params["instance_type"] = instance_type
    params["ami"] = get_ami(profile)
    if instance_profile:
        params["instance_profile"] = instance_profile
    if key_pair:
        params["key_pair"] = key_pair
    if security_groups:
        params["security_groups"] = security_groups
    if user_data:
        params["user_data"] = user_data
    if public_ip:
        params["public_ip"] = public_ip
    response = launchconfiguration.create(**params)  # returns nothing
    if aws_reporter:
        aws_reporter(reports, response)
    result = None
    try:
        result = response["ResponseMetadata"]["HTTPStatusCode"]
    except KeyError:
        msg = "Bad response to request."
        if job_error_reporter:
            job_error_reporter(reports, msg)
        if stderr_reporter:
            stderr_reporter(reports, msg)
        raise BadResponse(msg)
    if result == 200:
        result = "Launch configuration created."
    else:
        msg = "Launch configuration '" + str(name) + "' not created."
        if job_error_reporter:
            job_error_reporter(reports, msg)
        if stderr_reporter:
            stderr_reporter(reports, msg)
        raise ResourceNotCreated(msg)
    if job_text_reporter:
        job_text_reporter(reports, result)
    if stdout_reporter:
        stdout_reporter(reports, result)
    return True


def create_full(
        profile,
        name,
        instance_type,
        vpc=None,
        instance_profile=None,
        security_groups=None,
        key_pair=None,
        user_data=None,
        public_ip=None,
        reports=None,
        aws_reporter=None,
        job_heading_reporter=None,
        job_data_reporter=None,
        job_text_reporter=None,
        job_warning_reporter=None,
        job_error_reporter=None,
        stdout_reporter=None,
        stderr_reporter=None):
    """Create a launch configuration, with full checks.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name you want to give to the security group.

        instance_type
            An EC2 instance type, e.g., "m3.medium" or "t2.micro".
            Note that not all instance types work: m1 doesn't work
            with ECS, and t2.micro only works inside a VPC, for example.

        vpc
            The ID of a VPC you want to create the group in.

        instance_profile
            An ECS-enabled instance profile.

        security_groups
            A list of security group IDs.

        key_pair
            A key pair for the EC2 instances.

        user_data
            An init script for the EC2 instances.

        public_ip
            Assign a public IP to the instances?
            Should be ``True`` only inside a VPC.

        reports
            A list of reports to send info to.

        aws_reporter
            AWS responses will be sent to this reporter.

        job_heading_reporter
            Job headings will be sent to this reporter.

        job_data_reporter
            Job data structures will be sent to this reporter.

        job_text_reporter
            Simple text strings from jobs will be sent to this reporter.

        job_warning_reporter
            Job warnings will be sent to this reporter.

        job_error_reporter
            Job errors will be sent to this reporter.

        stdout_reporter
            Info meant for STDOUT will be sent to this reporter.

        stderr_reporter
            Info meant for STDERR will be sent to this reporter.

    Return:
        The AWS record for the launch configuration.

    """
    reporters = {}
    reporters["reports"] = reports
    reporters["aws_reporter"] = aws_reporter
    reporters["job_heading_reporter"] = job_heading_reporter
    reporters["job_data_reporter"] = job_data_reporter
    reporters["job_text_reporter"] = job_text_reporter
    reporters["job_warning_reporter"] = job_warning_reporter
    reporters["job_error_reporter"] = job_error_reporter
    reporters["stdout_reporter"] = stdout_reporter
    reporters["stderr_reporter"] = stderr_reporter

    # Check if the launch configuration exists already.
    params = {}
    params["profile"] = profile
    params["name"] = name
    params.update(reporters)
    result = fetch.get_by_name(**params)
    if result:
        msg = "Launch configuration '" + name + "' already exists."
        if job_error_reporter:
            job_error_reporter(reports, msg)
        if stderr_reporter:
            stderr_reporter(reports, msg)
        raise ResourceAlreadyExists(msg)

    # Create the launch configuration.
    params = {}
    params["profile"] = profile
    params["name"] = name
    params["instance_type"] = instance_type
    if instance_profile:
        params["instance_profile"] = instance_profile
    if key_pair:
        params["key_pair"] = key_pair
    if security_groups:
        params["security_groups"] = security_groups
    if user_data:
        params["user_data"] = user_data
    if public_ip:
        params["public_ip"] = public_ip
    params.update(reporters)
    create(**params)