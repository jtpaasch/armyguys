# -*- coding: utf-8 -*-

"""For creating and managing ECS task definitions."""

from polarexpress.aws.elasticbeanstalk import application
from polarexpress.aws import profile

from polarexpress.tasks import utils



def create_application(
        aws_profile,
        name):
    """Create an Elastic Beanstalk application.

    Args:

        aws_profile
            A profile to connect to AWS with.

        name
            A name to give to the application.

    """
    utils.heading("Creating application")
    params = {}
    params["profile"] = aws_profile
    params["name"] = name
    response = application.create(**params)
    utils.echo_data(response)

    # Exit nicely.
    utils.echo("")
    utils.echo("Done.")


def delete_application(
        aws_profile,
        application_name):
    """Delete an Elastic Beanstalk application.

    Args:

        aws_profile
            A profile to connect to AWS with.

        application_name
            The name of the application you want to delete.

    """
    utils.heading("Deleting application")
    params = {}
    params["profile"] = aws_profile
    params["application"] = application_name
    response = application.delete(**params)
    utils.echo_data(response)

    # Exit nicely.
    utils.echo("")
    utils.echo("Done.")


if __name__ == "__main__":
    # Get an AWS profile.
    aws_profile = profile.configured()

    # Set up some parameters.
    application_name = "sally"

    # Delete the application.
    # delete_application(aws_profile=aws_profile, application_name=application_name)
    # utils.exit()    
    
    # Or, create it.
    create_application(
        aws_profile=aws_profile,
        name=application_name)
