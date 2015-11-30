# -*- coding: utf-8 -*-

"""Utilities for working with Amazon's Elastic Beanstalk."""

from .. import client as boto3client

from . import utils


def create(profile, name, application, cname=None, version=None,
           tier="web", key_pair=None, instance_type="t1.micro",
           instance_profile=None, service_role=None,
           healthcheck_url=None, security_groups=None,
           max_instances=1, min_instances=1, tags=None,
           vpc_id=None, subnets=None, db_subnets=None,
           elb_subnets=None, elb_scheme=None,
           public_ip=None):
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
            You MUST have an instance profile if you're using ECS.

        service_role
            The name of a service role.

        healthcheck_url
            A URL to do health checks against.

        security_groups
            A list of security group names for the environment. Elastic
            Beanstalk will still create its own security group in addition
            to whatever you provide here.

        max_instances
            The maximum number of EC2 instances to scale to.

        min_instances
            The minimum number of EC2 instances to scale to.

        tags
            A list of {"Key": <key>, "Value": <value>} dicts to add to
            resources in the environment.

        vpc_id
            The ID of the VPC you want to launch the environment into.
            If you specify a VPC, you must fill in the ``subnets`` parameter.

        subnets
            A list of VPC subnets you want to launch the environment into.
            If you specify a ``vpc_id`` parameter, you must specify these too.

        db_subnets
            A list of DB subnets. Only applicable inside a VPC.

        elb_subnets
            A list of Elastic Load Balancer subnets. Only applicable
            inside a VPC.

        elb_scheme
            Set to ``internal`` if you want an internal load balancer.
            Otherwise, leave it blank for a public load balancer.
            Only applicable inside a VPC.

         public_ip
            Assign public IP addresses to the EC2 instances?

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("elasticbeanstalk", profile)
    params = {}
    params["ApplicationName"] = application
    params["EnvironmentName"] = name
    if cname:
        params["CNAMEPrefix"] = cname
    if version:
        params["VersionLabel"] = version
    stack = utils.get_multicontainer_docker_solution_stack(profile)
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
    if tags:
        params["Tags"] = tags
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
            "OptionName": "SecurityGroups",
            "Value": ",".join(security_groups),
        }
        options.append(security_groups_option)
    if min_instances:
        min_instances_option = {
            "Namespace": "aws:autoscaling:asg",
            "OptionName": "MinSize",
            "Value": str(min_instances),
        }
        options.append(min_instances_option)
    if max_instances:
        max_instances_option = {
            "Namespace": "aws:autoscaling:asg",
            "OptionName": "MaxSize",
            "Value": str(max_instances),
        }
        options.append(max_instances_option)
    if vpc_id:
        vpc_id_option = {
            "Namespace": "aws:ec2:vpc",
            "OptionName": "VPCId",
            "Value": vpc_id,
        }
        options.append(vpc_id_option)
    if subnets:
        subnets_option = {
            "Namespace": "aws:ec2:vpc",
            "OptionName": "Subnets",
            "Value": ",".join(subnets),
        }
        options.append(subnets_option)
    if db_subnets:
        db_subnets_option = {
            "Namespace": "aws:ec2:vpc",
            "OptionName": "DBSubnets",
            "Value": ",".join(db_subnets),
        }
        options.append(db_subnets_option)
    if elb_subnets:
        elb_subnets_option = {
            "Namespace": "aws:ec2:vpc",
            "OptionName": "ELBSubnets",
            "Value": ",".join(elb_subnets),
        }
        options.append(elb_subnets_option)
    if elb_scheme:
        elb_scheme_option = {
            "Namespace": "aws:ec2:vpc",
            "OptionName": "ELBScheme",
            "Value": elb_scheme,
        }
        options.append(elb_scheme_option)
    if public_ip:
        public_ip_option = {
            "Namespace": "aws:ec2:vpc",
            "OptionName": "AssociatePublicIpAddress",
            "Value": str(public_ip),
        }
        options.append(public_ip_option)
    if options:
        params["OptionSettings"] = options
    return client.create_environment(**params)


def delete(profile, environment, force=True):
    """Delete an Elastic Beanstalk environment.

    Args:

        profile
            A profile to connect to AWS with.

        environment
            The name of the environment to delete.

        force
            Terminate resources too?

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("elasticbeanstalk", profile)
    params = {}
    params["EnvironmentName"] = environment
    params["TerminateResources"] = force
    return client.terminate_environment(**params)
