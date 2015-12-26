# -*- coding: utf-8 -*-

"""Tools to help with running jobs."""

import sys

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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
        if status_code not in [200, 204]:
            msg = "Response code was not 200 OK."
            raise Non200Response

    return response


def create_mime_multipart_archive(files=None, raw_contents=None):
    """Create a MIME MultiPart Archive of files and file contents.

    Args:

        files
            A list of {"filepath": path, "contenttype": type} entries.

        raw_contents
            A list of {"contents": contents, "contenttype": type} entries.

    Returns:
        The archive text.

    """
    combined_message = MIMEMultipart()
    default_encoding = sys.getdefaultencoding()
    if files:
        for record in files:
            file_path = record["filepath"]
            content_type = record["contenttype"]
            with open(file_path, "rb") as f:
                contents = f.read()
                message = MIMEText(
                    contents,
                    content_type,
                    default_encoding)
                message.add_header(
                    "Content-Disposition",
                    "attachment; filename=\"%s\"" % (file_path))
                combined_message.attach(message)
    if raw_contents:
        counter = 1
        for record in raw_contents:
            filename = "user-data-" + str(counter)
            contents = record["contents"]
            content_type = record["contenttype"]
            message = MIMEText(
                contents,
                content_type,
                default_encoding)
            message.add_header(
                "Content-Disposition",
                "attachment; filename=\"%s\"" % (filename))
            combined_message.attach(message)
            counter += 1
    return combined_message.as_string()
