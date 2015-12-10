# -*- coding: utf-8 -*-

"""Tools to help with running jobs."""

from .exceptions import BadResponse
from .exceptions import MissingDataInResponse
from .exceptions import Non200Response


def check_response_is_ok(
        response,
        reports=None,
        aws_reporter=None,
        job_error_reporter=None,
        stdout_reporter=None):
    """Check that an AWS response is okay.

    Args:

        response
            The data returned by AWS.

        reports
            A list of reports to send info to.

        aws_reporter
            The AWS response will be sent to this reporter.

        job_error_reporter
            Job errors will be sent to this reporter.

        stderr_reporter
            Info meant for STDERR will be sent to this reporter.

    """
    if aws_reporter:
        aws_reporter(reports, response)
    try:
        status_code = response["ResponseMetadata"]["HTTPStatusCode"]
    except KeyError:
        msg = "Could not find status code in response."
        if job_error_reporter:
            job_error_reporter(reports, msg)
        if stderr_reporter:
            stderr_reporter(reports, msg)
        raise BadResponse(msg)
    if status_code != 200:
        msg = "Response code was not 200 OK."
        if job_error_reporter:
            job_error_reporter(reports, msg)
        if stderr_reporter:
            stderr_reporter(reports, msg)
        raise Non200Response


def get_data_in_response(
        key,
        response,
        reports=None,
        aws_reporter=None,
        job_error_reporter=None,
        stdout_reporter=None):
    """Check that an AWS response is okay.

    Args:

        key
            The key to the data you're looking for.

        response
            The data returned by AWS.

        reports
            A list of reports to send info to.

        aws_reporter
            The AWS response will be sent to this reporter.

        job_error_reporter
            Job errors will be sent to this reporter.

        stderr_reporter
            Info meant for STDERR will be sent to this reporter.

    Returns:
        The requested data.

    """
    data = None
    try:
        data = response[key]
    except KeyError:
        msg = "No '" + key + "' in response."
        if job_error_reporter:
            job_error_reporter(reports, msg)
        if stderr_reporter:
            stderr_reporter(reports, msg)
        raise MissingDataInResponse(msg)
    return data
