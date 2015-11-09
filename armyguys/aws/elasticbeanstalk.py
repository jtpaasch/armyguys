# -*- coding: utf-8 -*-

"""Utilities for working with Amazon's Elastic Beanstalk."""

from . import client as boto3client


def get_solution_stacks(profile):
    """Get a list of all available solution stacks.

    Args:

        profile
            A profile to connect to AWS with.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("elasticbeanstalk", profile)
    return client.list_available_solution_stacks()


def get_multicontainer_docker_solution_stack(profile):
    """Get the multi-container Docker solution stack.

    This calls ``get_solution_stacks()``, and then steps through the list
    until it finds the multi-container Docker 1.7.1 one.

    Note:
        This method needs to be checked/updated somehow. If Amazon suddenly
        changes their stack to, say, Docker 1.7.2, this method won't work
        anymore, because it's looking for 1.7.1 exactly.

    Args:

        profile
            A profile to connect to AWS with.

    Returns:
        The JSON data for the multi-container Docker 1.7.1 solution stack.

    """
    response = get_solution_stacks(profile)
    stacks = response.get("SolutionStacks")
    match = "Multi-container Docker 1.7.1"
    items_with_match = (x for x in stacks if match in x)
    return next(items_with_match, None)


def create_application(profile, name):
    """Create an Elastic Beanstalk application.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name to give the application.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("elasticbeanstalk", profile)
    params = {}
    params["ApplicationName"] = name
    return client.create_application(**params)


def delete_application(profile, name, force=True):
    """Delete an Elastic Beanstalk application.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name of the application to delete.

        force
            Terminate the environment too?

    """
    client = boto3client.get("elasticbeanstalk", profile)
    params = {}
    params["ApplicationName"] = name
    params["TerminateEnvByForce"] = force
    return client.delete_application(**params)


def create_application_version(profile, application, version, s3bucket, s3key):
    """Create a new version of an application.

    Args:

        profile
            A profile to connect to AWS with.

        application
            The name of the application to create a version for.

        version
            The name/label of the version, e.g., "v1.0" or "1.0.0".

        s3bucket
            The name of the S3 bucket with a Dockerrun.aws.json file.

        s3key
            The name of the Dockerrun.aws.json file.
            TO DO: Is the name redundant? Will it always be Dockerrun.aws.json,
            or can we version it?

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("elasticbeanstalk", profile)
    params = {}
    params["ApplicationName"] = application
    params["VersionLabel"] = version
    params["SourceBundle"] = {
        "S3Bucket": s3bucket,
        "S3Key": s3key,
        }
    return client.create_application_version(**params)


def delete_application_version(profile, application, version, delete_source_file=True):
    """Delete an application version.

    Args:

        profile
            A profile to connect to AWS with.

        application
            The name of the application to delete the version for.

        version
            The name/label of the version to delete, e.g., "v1.0" or "1.0.0".

        delete_source_file
            Delete the source file from S3?

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("elasticbeanstalk", profile)
    params = {}
    params["ApplicationName"] = application
    params["VersionLabel"] = version
    params["DeleteSourceBundle"] = delete_source_file
    return client.delete_application_version(**params)


def create_environment(profile, name, application, cname=None, version=None,
                       tier="web", key_pair=None, instance_type="t2.micro",
                       instance_profile=None, service_role=None,
                       healthcheck_url=None, security_groups=None):
    """Create a multi-container Docker Elastic Beanstalk environment.

    Note: 
        This function will automatically select the multi-container
        Docker 1.7.1 stack to use as a template for the environment.
        TO DO: This needs to be checked, as that can break. See the
        note above under ``get_multicontainer_docker_solution_stack()``.

    Note:
        The ``profile`` and ``role`` options are crucial. Docker cannot
        run correctly if it doesn't have them.
        TO DO: The creation and assignment of these needs to be automated.

    Note:
        Information about the tier definitions is hard to find in
        Amazon's documentation. Look in the API and CloudFormation
        docs for details. With a little work, information can
        sometimes be gleaned from there.

    Note:
        Information about the OPTIONS you can add or remove can be found
        at the Elastic Beanstalk developer guide, under "Environment
        Configuration." All the sub pages have options, especially under
        Amazon CLI examples.

    Args:

        profile
            A profile to connect to AWS with.

        name
            A name to give to the environment.

        application
            The name of the application to deploy into this environment.

        cname
            The CName to give to the application. This determines the
            application's URL. If ``cname`` is ``foo``, for example,
            the URL will be ``foo.elasticbeanstalk.com``. The CName
            must be unique to all Amazon customers, since it's a
            public-facing URL.

        version
            The name/label of the version to launch in this environment.

        tier
            Must be "web" or "worker" (the default is "web"). This
            determines if the application is a web or a worker type
            application.

        key_pair
            The name of a key pair to use to connect to EC2 instances
            that get launched into the environment.

        instance_type
            The type of EC2 instance to launch, when EC2 instances get
            launched (the launching is handled automatically by Amazon).

        instance_profile
            The name of an IAM Instance Profile.
            TO DO: We need to automate the creation of this profile.

        service_role
            The name of a service role.
            TO DO: We need to automate the creation of this role.

        healthcheck_url
            A URL to do health checks against.

        security_groups
            A list of security groups for the EC2 instances that get
            launched into the environment.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("elasticbeanstalk", profile)
    params = {}
    params["ApplicationName"] = application
    params["EnvironmentName"] = name
    if not cname:
        cname = application
    params["CNAMEPrefix"] = cname
    if version:
        params["VersionLabel"] = version
    stack = get_multicontainer_docker_solution_stack(profile)
    params["SolutionStackName"] = stack        
    if tier == "web":
        tier_definition = {
            "Name": "WebServer",
            "Type": "Standard",
            "Version": "1.0",
        }
    elif tier == "worker":
        tier_definition = {
            "Name": "Worker",
            "Type": "SQS/HTTP",
            "Version": "1.0",
        }
    else:
        raise Exception("tier must be 'web' or 'worker'")
    params["Tier"] = tier_definition
    options = []
    if key_pair:
        key_pair_option = {
            "Namespace": "aws:autoscaling:launchconfiguration",
            "OptionName": "EC2KeyName",
            "Value": key_pair,
        }
        options.append(key_pair_option)
    if instance_type:
        instance_type_option = {
            "Namespace": "aws:autoscaling:launchconfiguration",
            "OptionName": "InstanceType",
            "Value": instance_type,
        }
        options.append(instance_type_option)
    if instance_profile:
        profile_option = {
            "Namespace": "aws:autoscaling:launchconfiguration",
            "OptionName": "IamInstanceProfile",
            "Value": instance_profile,
        }
        options.append(profile_option)
    if service_role:
        role_option = {
            "Namespace": "aws:elasticbeanstalk:environment",
            "OptionName": "ServiceRole",
            "Value": service_role,
        }
        options.append(role_option)
    if healthcheck_url:
        healthcheck_url_option = {
            "Namespace": "aws:elasticbeanstalk:application",
            "OptionName": "Application Healthcheck URL",
            "Value": healthcheck_url,
        }
        options.append(healthcheck_url_option)
    if security_groups:
        security_groups_option = {
            "Namespace": "aws:autoscaling:launchconfiguration",
            "OptionName": "SecurityGroupIds",
            "Value": security_groups,
        }
        options.append(security_groups_option)
    if options:
        params["OptionSettings"] = options
    return client.create_environment(**params)


def delete_environment(profile, name, force=True):
    """Delete an Elastic Beanstalk environment.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name of the environment to delete.

        force
            Terminate resources too?

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("elasticbeanstalk", profile)
    params = {}
    params["EnvironmentName"] = name
    params["TerminateResources"] = force
    return client.terminate_environment(**params)
