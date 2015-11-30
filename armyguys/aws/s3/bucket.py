# -*- coding: utf-8 -*-

"""Utilities for working with S3."""

from os import path
from .. import client as boto3client


def get_eb_bucket(profile):
    """Get the S3 bucket Elastic Beanstalk uses for storage.

    Note:
        Elastic Beanstalk handles the creation and management
        of this bucket. You only need to use this method to
        get the name of the bucket.

    Args:

        profile
            A profile to connect to AWS with.

    Returns:
        The JSON response returned by boto3, including the bucket name.

    """
    client = boto3client.get("elasticbeanstalk", profile)
    return client.create_storage_location()


def create(profile, name, private=False):
    """Create an S3 bucket.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name to give to the bucket.

        private
            Should the bucket be private?

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("s3", profile)
    params = {}
    params["Bucket"] = name
    if private:
        params["ACL"] = "private"
    return client.create_bucket(**params)


def delete(profile, bucket):
    """Delete an S3 bucket.

    Args:

        profile
            A profile to connect to AWS with.

        bucket
            The name of the bucket to delete.

    """
    client = boto3client.get("s3", profile)
    params = {}
    params["Bucket"] = bucket
    return client.delete_bucket(**params)
