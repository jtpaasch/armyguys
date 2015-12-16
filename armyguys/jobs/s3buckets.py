# -*- coding: utf-8 -*-

"""Jobs for S3 buckets."""

from ..aws.s3 import bucket

from .exceptions import WaitTimedOut
from .exceptions import ResourceAlreadyExists
from .exceptions import ResourceDoesNotExist
from .exceptions import ResourceNotCreated
from .exceptions import ResourceNotDeleted

from . import utils


def get_display_name(record):
    """Get the display name for a record.

    Args:

        record
            A record returned by AWS.

    Returns:
        A display name for the bucket.

    """
    return record["Name"]


def fetch_all(profile):
    """Fetch all s3 buckets.

    Args:

        profile
            A profile to connect to AWS with.

    Returns:
        A list of VPCs.

    """
    params = {}
    params["profile"] = profile
    response = utils.do_request(bucket, "get", params)
    data = utils.get_data("Buckets", response)
    return data


def fetch_by_name(profile, name):
    """Fetch a bucket by name.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name of the bucket you want to fetch.

    Returns:
        A list of buckets with the provided name.

    """
    buckets = fetch_all(profile)
    return [x for x in buckets if x["Name"] == name]


def fetch_beanstalk_bucket(profile):
    """Fetch an elastic beanstalk bucket.

    Note:
        AWS handles the creation and management of this bucket.
        All you have to do is call this function to get its name.

    Args:

        profile
            A profile to connect to AWS with.

    Returns:
        An elastic beanstalk bucket.

    """
    params = {}
    params["profile"] = profile
    response = utils.do_request(bucket, "get_eb_bucket", params)
    data = utils.get_data("S3Bucket", response)
    return data


def is_bucket(profile, name):
    """Check if a bucket exists.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name of a bucket.

    Returns:
        True if it exists, False if it doesn't.

    """
    result = fetch_by_name(profile, name)
    return len(result) > 0


def polling_fetch(profile, name, max_attempts=10, wait_interval=1):
    """Try to fetch a bucket repeatedly until it exists.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name of the bucket you want to fetch.

        max_attempts
            The max number of times to poll AWS.

        wait_interval
            How many seconds to wait between each poll.

    Returns:
        The bucket's info, or None if it times out.

    """
    data = None
    count = 0
    while count < max_attempts:
        data = fetch_by_name(profile, name)
        from pprint import pprint; pprint(data)
        if data:
            break
        else:
            count += 1
            sleep(wait_interval)
    if not data:
        msg = "Timed out waiting for bucket to be created."
        raise WaitTimedOut(msg)
    return data


def create(profile, name, private=None):
    """Create an S3 bucket.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name you want to give to the bucket.

        private
            True if you want it private. False if not.

    Returns:
        The newly created bucket's name.

    """
    # Make sure the bucket doesn't already exist.
    if is_bucket(profile, name):
        msg = "The bucket '" + str(name) + "' already exists."
        raise ResourceAlreadyExists(msg)
    
    # Now we can create it.
    params = {}
    params["profile"] = profile
    params["name"] = name
    if private == True:
        params["private"] = True
    response = utils.do_request(bucket, "create", params)

    # Now check that it exists.
    bucket_data = None
    try:
        bucket_data = polling_fetch(profile, name)
    except WaitTimedOut:
        msg = "Timed out waiting for '" + str(name) + "' to be created."
        raise ResourceNotCreated(msg)
    if not bucket_data:
        msg = "Bucket '" + str(name) + "' not created."
        raise ResourceNotCreated(msg)

    # Send back the bucket's data.
    return bucket_data


def delete(profile, name):
    """Delete an S3 bucket.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name of the bucket you want to delete.

    """
    # Make sure it exists before we try to delete it.
    s3_bucket = fetch_by_name(profile, name)
    if not s3_bucket:
        msg = "No bucket '" + str(name) + "'."
        raise ResourceDoesNotExist(msg)

    # Now try to delete it.
    params = {}
    params["profile"] = profile
    params["bucket"] = name
    response = utils.do_request(bucket, "delete", params)

    # Check that it was, in fact, deleted.
    s3_bucket = fetch_by_name(profile, name)
    if s3_bucket:
        msg = "Bucket '" + str(name) + "' was not deleted."
        raise ResourceNotDeleted(msg)
