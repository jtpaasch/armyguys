# -*- coding: utf-8 -*-

"""Utilities for working with S3."""

from os import path
from .. import client as boto3client


def create(profile, bucket, key, contents=None, filepath=None):
    """Upload a file to an S3 bucket.

    Args:

        profile
            A profile to connect to AWS with.

        bucket
            The name of the bucket to upload the file to.

        key
            The key/name to give to the file in S3.

        contents
            The contents of the file you want to upload.
            You must specify this OR a filepath.

        filepath
            The path to the file you want to upload.
            You must specify this OR a filepath.

    Returns:
        The JSON response returned by boto3.

    """
    if filepath:
        norm_path = path.normpath(filepath)
        norm_path = norm_path.rstrip(path.sep)
        with open(norm_path, "rb") as f:
            data = f.read()
    elif contents:
        data = contents
    client = boto3client.get("s3", profile)
    params = {}
    params["Body"] = data
    params["Bucket"] = bucket
    params["Key"] = key
    return client.put_object(**params)


def delete(profile, key, bucket):
    """Delete a file from an S3 bucket.

    Args:

        profile
            A profile to connect to AWS with.

        key
            The name of the file you want to delete.

        bucket
            The bucket to delete the file from.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("s3", profile)
    params = {}
    params["Key"] = key
    params["Bucket"] = bucket
    return client.delete_object(**params)


def get(profile, bucket, prefix=None):
    """Get all files in an S3 bucket.

    Args:

        profile
            A profile to connect to AWS with.

        bucket
            The name of the bucket to fetch files from.

        prefix
            Limit the search to files that begin with this.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("s3", profile)
    params = {}
    params["Bucket"] = bucket
    if prefix:
        params["Prefix"] = prefix
    return client.list_objects(**params)
