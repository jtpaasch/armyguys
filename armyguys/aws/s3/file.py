# -*- coding: utf-8 -*-

"""Utilities for working with S3."""

from os import path
from .. import client as boto3client


def create(profile, s3bucket, s3key, contents=None, filepath=None):
    """Upload a file to an S3 bucket.

    Args:

        profile
            A profile to connect to AWS with.

        s3bucket
            The name of the bucket to upload the file to.

        s3key
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
    params["Bucket"] = s3bucket
    params["Key"] = s3key
    return client.put_object(**params)


def delete(profile, s3key, s3bucket):
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
