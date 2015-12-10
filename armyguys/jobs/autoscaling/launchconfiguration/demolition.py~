# -*- coding: utf-8 -*-

"""Jobs for deleting launch configurations.

For the latest list of ECS-optimized AMIs, try this page:
http://docs.aws.amazon.com/AmazonECS/latest/developerguide/launch_container_instance.html

"""

from ....aws import profile as profile_tools
from ....aws.autoscaling import launchconfiguration

from ...exceptions import BadResponse
from ...exceptions import ResourceAlreadyExists
from ...exceptions import ResourceDoesNotExist
from ...exceptions import TooManyRecords

from ... import utils

from . import fetch


def delete(
        profile,
        name,
        reports=None,
        aws_reporter=None,
        job_heading_reporter=None,
        job_data_reporter=None,
        job_text_reporter=None,
        job_warning_reporter=None,
        job_error_reporter=None,
        stdout_reporter=None,
        stderr_reporter=None):
    """Delete a launch configuration.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name of the launhc configuration you want to delete.

        reports
            A list of reports to send info to.

        aws_reporter
            AWS responses will be sent to this reporter.

        job_data_reporter
            Job data structures will be sent to this reporter.

        job_text_reporter
            Simple text strings from jobs will be sent to this reporter.

        job_warning_reporter
            Job warnings will be sent to this reporter.

        job_error_reporter
            Job errors will be sent to this reporter.

        stdout_reporter
            Info meant for STDOUT will be sent to this reporter.

        stderr_reporter
            Info meant for STDERR will be sent to this reporter.

    Return:
        The data returned by AWS, or None if none were found.

    """
    if job_heading_reporter:
        job_heading_reporter(reports, "Deleting launch configuration")
    params = {}
    params["profile"] = profile
    params["launch_configuration"] = name
    response = launchconfiguration.delete(**params)
    utils.check_response_is_ok(
        response,
        reports,
        aws_reporter,
        job_error_reporter,
        stderr_reporter)
    result = "Launch configuration deleted."
    if job_text_reporter:
        job_text_reporter(reports, result)
    if stdout_reporter:
        stdout_reporter(reports, result)
    return True


def delete_full(
        profile,
        name,
        reports=None,
        aws_reporter=None,
        job_heading_reporter=None,
        job_data_reporter=None,
        job_text_reporter=None,
        job_warning_reporter=None,
        job_error_reporter=None,
        stdout_reporter=None,
        stderr_reporter=None):
    """Delete a launch configuration, with full checks.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name of the launch configuration you want to delete.

        reports
            A list of reports to send info to.

        aws_reporter
            AWS responses will be sent to this reporter.

        job_heading_reporter
            Job headings will be sent to this reporter.

        job_data_reporter
            Job data structures will be sent to this reporter.

        job_text_reporter
            Simple text strings from jobs will be sent to this reporter.

        job_warning_reporter
            Job warnings will be sent to this reporter.

        job_error_reporter
            Job errors will be sent to this reporter.

        stdout_reporter
            Info meant for STDOUT will be sent to this reporter.

        stderr_reporter
            Info meant for STDERR will be sent to this reporter.

    Return:
        The AWS record for the launch configuration.

    """
    reporters = {}
    reporters["reports"] = reports
    reporters["aws_reporter"] = aws_reporter
    reporters["job_heading_reporter"] = job_heading_reporter
    reporters["job_data_reporter"] = job_data_reporter
    reporters["job_text_reporter"] = job_text_reporter
    reporters["job_warning_reporter"] = job_warning_reporter
    reporters["job_error_reporter"] = job_error_reporter
    reporters["stdout_reporter"] = stdout_reporter
    reporters["stderr_reporter"] = stderr_reporter

    # Check if the launch configuration exists already.
    params = {}
    params["profile"] = profile
    params["name"] = name
    params.update(reporters)
    result = fetch.get_by_name(**params)
    if not result:
        msg = "No such launch configuration '" + name + "'."
        if job_error_reporter:
            job_error_reporter(reports, msg)
        if stderr_reporter:
            stderr_reporter(reports, msg)
        raise ResourceDoesNotExist(msg)

    # Delete the launch configuration.
    params = {}
    params["profile"] = profile
    params["name"] = name
    params.update(reporters)
    delete(**params)

    # Check that it's gone.
    params = {}
    params["profile"] = profile
    params["name"] = name
    params.update(reporters)
    result = fetch.get_by_name(**params)
    if result:
        msg = "Launch configuration '" + name + "' not deleted."
        if job_error_reporter:
            job_error_reporter(reports, msg)
        if stderr_reporter:
            stderr_reporter(reports, msg)
        raise ResourceNotDeleted(msg)
