# -*- coding: utf-8 -*-

"""Tools to help with running jobs."""

from botocore.exceptions import ClientError

from .exceptions import AwsError
from .exceptions import MissingKey
from .exceptions import Non200Response
from .exceptions import PermissionDenied


def get_data(key, response):
    """Extract some data from a response.

    Args:

        key
            The key to the data you're looking for.

        response
            The data to look in.

    Raises:
        ``MissingKey`` if it can't find the key.

    Returns:
        The requested data.

    """
    data = None
    try:
        data = response[key]
    except KeyError:
        msg = "No '" + key + "' in response."
        raise MissingKey(msg)
    return data


def do_request(package, method, params, error_handler=None):
    """Perform an AWS request.

    Args:

        package
            The package that implements a boto3 request.

        method
            The method/function in the package to call.

        params
            A dict of kwargs to pass to the method.

        error_handler
            A function to handle AWS errors.

    Returns:
        The response returned by AWS.

    """
    func = getattr(package, method)
    response = None
    if not params:
        params = {}
    try:
        response = func(**params)
    except ClientError as error:
        http_code = error.response["ResponseMetadata"]["HTTPStatusCode"]
        error_code = error.response["Error"]["Code"]
        message = error.response["Error"]["Message"]

        if error_code == "UnauthorizedOperation":
            msg = "You do not have permission to do this."
            raise PermissionDenied(msg)
        elif error_handler:
            error_handler(error)
        else:
            raise AwsError(message)

    if response:
        try:
            status_code = response["ResponseMetadata"]["HTTPStatusCode"]
        except KeyError:
            msg = "Could not find status code in response."
            raise MissingKey(msg)
        if status_code != 200:
            msg = "Response code was not 200 OK."
            raise Non200Response

    return response
