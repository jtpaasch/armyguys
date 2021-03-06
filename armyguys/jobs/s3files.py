# -*- coding: utf-8 -*-

"""Jobs for S3 files."""

import os

from ..aws.s3 import file as s3file

from .exceptions import FileDoesNotExist
from .exceptions import ImproperlyConfigured
from .exceptions import MissingKey
from .exceptions import ResourceAlreadyExists
from .exceptions import ResourceDoesNotExist
from .exceptions import ResourceNotCreated
from .exceptions import ResourceNotDeleted
from .exceptions import WaitTimedOut

from . import s3buckets
from . import utils


def get_display_name(record):
    """Get the display name for a record.

    Args:

        record
            A record returned by AWS.

    Returns:
        A display name for the bucket.

    """
    return record["Key"]


def fetch_all(profile, bucket):
    """Fetch all files in an S3 bucket.

    Args:

        profile
            A profile to connect to AWS with.

        bucket
            The name of the bucket you want to fetch files from.

    Returns:
        A list of S3 files.

    """
    if not s3buckets.exists(profile, bucket):
        msg = "No bucket '" + str(bucket) + "'."
        raise ResourceDoesNotExist(msg)

    params = {}
    params["profile"] = profile
    params["bucket"] = bucket
    response = utils.do_request(s3file, "get", params)
    data = utils.get_data("Contents", response)
    return data


def fetch_by_name(profile, bucket, name):
    """Fetch a file by name.

    Args:

        profile
            A profile to connect to AWS with.

        bucket
            The name of the bucket you want to fetch files from.

        name
            The name of the file you want to fetch.

    Returns:
        A list of files with the provided name.

    """
    if not s3buckets.exists(profile, bucket):
        msg = "No bucket '" + str(bucket) + "'."
        raise ResourceDoesNotExist(msg)

    params = {}
    params["profile"] = profile
    params["bucket"] = bucket
    params["prefix"] = name
    response = utils.do_request(s3file, "get", params)

    try:
        data = utils.get_data("Contents", response)
    except MissingKey:
        data = []
    return [x for x in data if x["Key"] == name]


def exists(profile, bucket, name):
    """Check if a file exists in an S3 bucket.

    Args:

        profile
            A profile to connect to AWS with.

        bucket
            The name of the bucket you want to find the file in.

        name
            The name of a file.

    Returns:
        True if it exists, False if it doesn't.

    """
    result = fetch_by_name(profile, bucket, name)
    return len(result) > 0


def polling_fetch(profile, bucket, name, max_attempts=10, wait_interval=1):
    """Try to fetch a file in a bucket repeatedly until it exists.

    Args:

        profile
            A profile to connect to AWS with.

        bucket
            The name of the bucket you want to find the file in..

        name
            The name of the file you want to fetch.

        max_attempts
            The max number of times to poll AWS.

        wait_interval
            How many seconds to wait between each poll.

    Returns:
        The file's info, or None if it times out.

    """
    data = None
    count = 0
    while count < max_attempts:
        data = fetch_by_name(profile, bucket, name)
        if data:
            break
        else:
            count += 1
            sleep(wait_interval)
    if not data:
        msg = "Timed out waiting for file to be created."
        raise WaitTimedOut(msg)
    return data


def create(profile, bucket, name, filepath=None, contents=None):
    """Create an S3 bucket.

    Args:

        profile
            A profile to connect to AWS with.

        bucket
            The name of the bucket you want to create the file in.

        name
            The name you want to give to the file.

        filepath
            The path to a file. If you provide this, leave
            the ``contents`` parameter blank.

        contents
            The contents of a file. If you provide this, leave
            the ``filepath`` parameter blank.

    Returns:
        Info about the newly created file.

    """
    # Make sure the bucket exists.
    if not s3buckets.exists(profile, bucket):
        msg = "No bucket '" + str(bucket) + "'."
        raise ResourceDoesNotExist(msg)

    # Make sure only contents or a filepath are specified.
    if all([filepath, contents]) or not any([filepath, contents]):
        msg = "Provide either a file path or its contents, but not both."
        raise ImproperlyConfigured(msg)

    # Make sure the file exists, if a filepath was specified.
    if filepath:
        if not os.path.isfile(filepath):
            msg = "No such file '" + str(filepath) + "'."
            raise FileDoesNotExist(msg)

    # Now we can create it.
    params = {}
    params["profile"] = profile
    params["bucket"] = bucket
    params["key"] = name
    if filepath:
        params["filepath"] = filepath
    elif contents:
        params["contents"] = contents
    response = utils.do_request(s3file, "create", params)

    # Now check that it exists.
    file_data = None
    try:
        file_data = polling_fetch(profile, bucket, name)
    except WaitTimedOut:
        msg = "Timed out waiting for '" + str(name) + "' to be created."
        raise ResourceNotCreated(msg)
    if not file_data:
        msg = "File '" + str(name) + "' not created."
        raise ResourceNotCreated(msg)

    # Send back the file's data.
    return file_data


def delete(profile, bucket, name):
    """Delete an S3 file.

    Args:

        profile
            A profile to connect to AWS with.

        bucket
            The name of the bucket you want to delete the file from.

        name
            The name of the file you want to delete.

    """
    # Make sure the bucket exists.
    if not s3buckets.exists(profile, bucket):
        msg = "No bucket '" + str(bucket) + "'."
        raise ResourceDoesNotExist(msg)

    # Make sure the file exists.
    if not exists(profile, bucket, name):
        msg = "No file '" + str(name) + "'."
        raise ResourceDoesNotExist(msg)

    # Now try to delete it.
    params = {}
    params["profile"] = profile
    params["bucket"] = bucket
    params["key"] = name
    response = utils.do_request(s3file, "delete", params)

    # Check that it was, in fact, deleted.
    if exists(profile, bucket, name):
        msg = "The file '" + str(name) + "' was not deleted."
        raise ResourceNotDeleted(msg)
