# -*- coding: utf-8 -*-

"""Utilities for working with Amazon's Elastic Beanstalk."""

from .. import client as boto3client

from . import utils


def create(profile, name):
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


def delete(profile, application, force=True):
    """Delete an Elastic Beanstalk application.

    Args:

        profile
            A profile to connect to AWS with.

        application
            The name of the application you want to delete.

        force
            Terminate the environment too?

    """
    client = boto3client.get("elasticbeanstalk", profile)
    params = {}
    params["ApplicationName"] = application
    params["TerminateEnvByForce"] = force
    return client.delete_application(**params)
