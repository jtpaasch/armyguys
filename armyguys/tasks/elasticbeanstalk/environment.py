# -*- coding: utf-8 -*-

"""For creating and managing ECS task definitions."""

from polarexpress.aws.elasticbeanstalk import environment
from polarexpress.aws import profile

from polarexpress.tasks import utils



def create_environment(
        aws_profile,
        application,
        version,
        name,
        cname=None,
        key_pair=None,
        instance_type=None,
        instance_profile=None,
        security_groups=None,
        healthcheck_url=None,
        max_instances=1,
        min_instances=1,
        tags=None,
        vpc_id=None,
        subnets=None,
        public_ip=None):
    """Launch an Elastic Beanstalk application version into an environment.

    Args:

        aws_profile
            A profile to connect to AWS with.

        application
            The name of an application.

        version
            The name/tag of the version you want to launch.

        name
            The name you want to give to the environment.

    """
    utils.heading("Creating environment")
    params = {}
    params["profile"] = aws_profile
    params["application"] = application
    params["version"] = version
    params["name"] = name
    if cname:
        params["cname"] = cname
    if key_pair:
        params["key_pair"] = key_pair
    if instance_type:
        params["instance_type"] = instance_type
    if instance_profile:
        params["instance_profile"] = instance_profile
    if security_groups:
        params["security_groups"] = security_groups
    if healthcheck_url:
        params["healthcheck_url"] = healthcheck_url
    if max_instances:
        params["max_instances"] = max_instances
    if min_instances:
        params["min_instances"] = min_instances
    if tags:
        params["tags"] = tags
    if vpc_id:
        params["vpc_id"] = vpc_id
    if subnets:
        params["subnets"] = subnets
    if public_ip:
        params["public_ip"] = public_ip
    response = environment.create(**params)
    utils.echo_data(response)

    # Exit nicely.
    utils.echo("")
    utils.echo("Done.")


def delete_environment(
        aws_profile,
        environment):
    """Delete an Elastic Beanstalk environment.

    Args:

        aws_profile
            A profile to connect to AWS with.

        environment
            The name of the environment you want to delete.

    """
    utils.heading("Deleting environment")
    params = {}
    params["profile"] = aws_profile
    params["environment"] = environment
    response = environment.delete(**params)
    utils.echo_data(response)

    # Exit nicely.
    utils.echo("")
    utils.echo("Done.")


if __name__ == "__main__":
    # Get an AWS profile.
    aws_profile = profile.configured()

    # Set up some parameters.
    application_name = "sally"
    version = "1.0"
    environment_name = "sally-env-kappa"
    instance_type = "t2.micro"
    key_pair = "quickly_fitchet"
    instance_profile = "ecs-instance-profile"
    vpc_id = None  # "vpc-b91299dd"
    subnets = None  # ["subnet-9905c3ef", "subnet-09929922"]
    security_groups = None  # ["sg-b3ecc9d5"]
    public_ip = None  # True

    # Delete the environment
    params = {}
    params["aws_profile"] = aws_profile
    params["environment"] = environment_name
    # delete_environment(**params)
    # utils.exit()    
    
    # Or, create it.
    params = {}
    params["aws_profile"] = aws_profile
    params["application"] = application_name
    params["version"] = version
    params["name"] = environment_name
    params["instance_type"] = instance_type
    params["key_pair"] = key_pair
    params["instance_profile"] = instance_profile
    params["vpc_id"] = vpc_id
    params["subnets"] = subnets
    params["security_groups"] = security_groups
    params["public_ip"] = public_ip
    create_environment(**params)
