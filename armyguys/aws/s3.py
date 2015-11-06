# -*- coding: utf-8 -*-

"""Utilities for working with S3."""

from os import path
from . import client as boto3client


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


def create_bucket(profile, name):
    """Create an S3 bucket.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name to give to the bucket.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("s3", profile)
    params = {}
    params["Bucket"] = name
    return client.create_bucket(**params)


def delete_bucket(profile, name):
    """Delete an S3 bucket.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name of the bucket to delete.

    """
    client = boto3client.get("s3", profile)
    params = {}
    params["Bucket"] = name
    return client.delete_bucket(**params)


def upload_to_bucket(profile, filepath, s3bucket):
    """Upload a file to an S3 bucket.

    Args:

        profile
            A profile to connect to AWS with.

        filepath
            The path to the file you want to upload.

        s3bucket
            The name of the bucket to upload the file to.

    Returns:
        The JSON response returned by boto3.

    """
    norm_path = path.normpath(filepath)
    norm_path = norm_path.rstrip(path.sep)
    with open(norm_path, "rb") as f:
        data = f.read()
    filename = path.split(norm_path)[1]
    client = boto3client.get("s3", profile)
    params = {}
    params["Body"] = data
    params["Bucket"] = s3bucket
    params["Key"] = filename
    return client.put_object(**params)


def delete_from_bucket(profile, s3key, s3bucket):
    """Delete a file from an S3 bucket.

    Args:

        profile
            A profile to connect to AWS with.

        s3key
            The name of the file you want to delete.

        s3bucket
            The bucket to delete the file from.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("s3", profile)
    params = {}
    params["Key"] = s3key
    params["Bucket"] = s3bucket
    return client.delete_object(**params)
