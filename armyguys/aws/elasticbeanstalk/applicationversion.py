# -*- coding: utf-8 -*-

"""Utilities for working with Amazon's Elastic Beanstalk."""

from .. import client as boto3client

from . import utils


def create(profile, application, name, s3bucket, s3key):
    """Create a new version of an application.

    Args:

        profile
            A profile to connect to AWS with.

        application
            The name of the application to create a version for.

        name
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
    params["VersionLabel"] = name
    params["SourceBundle"] = {
        "S3Bucket": s3bucket,
        "S3Key": s3key,
        }
    return client.create_application_version(**params)


def delete(profile, application, version, delete_source_file=True):
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
