# -*- coding: utf-8 -*-

"""Jobs for fetching auto scaling group data."""

from ....aws.autoscaling import autoscalinggroup

from ... import utils


def get_all(
        profile,
        reports=None,
        aws_reporter=None,
        job_heading_reporter=None,
        job_data_reporter=None,
        job_text_reporter=None,
        job_warning_reporter=None,
        job_error_reporter=None,
        stdout_reporter=None,
        stderr_reporter=None):
    """Get all auto scaling groups.

    Args:

        profile
            A profile to connect to AWS with.

        reports
            A list of reports to send info to.

        aws_reporter
            AWS responses will be sent to this reporter.

        job_heading_reporter
            Job headings will be sent to this reporter.

        job_data_reporter
            Job data structures will be sent to this reporter.

        job_text_reporter
            Text strings from jobs will be sent to this reporter.

        job_warning_reporter
            Job warnings will be sent to this reporter.

        job_error_reporter
            Job errors will be sent to this reporter.

        stdout_reporter
            Info meant for STDOUT will be sent to this reporter.

        stderr_reporter
            Info meant for STDERR will be sent to this reporter.
 
    Return:
        A list of security group records from AWS.

    """
    if job_heading_reporter:
        job_heading_reporter(reports, "Fetching auto scaling groups")
    params = {}
    params["profile"] = profile
    response = autoscalinggroup.get(**params)
    utils.check_response_is_ok(
        response,
        reports,
        aws_reporter,
        job_error_reporter,
        stderr_reporter)
    data = utils.get_data_in_response(
        "AutoScalingGroups",
        response,
        reports,
        job_error_reporter,
        stderr_reporter)
    result = []
    if len(data) > 0:
        result = data
    if job_data_reporter:
        job_data_reporter(reports, result)
    if stdout_reporter:
        stdout_reporter(reports, result)
    return result


def get_by_name(
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
    """Get all launch configurations.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name of the launch configuration you want to fetch.

        reports
            A list of reports to send info to.

        aws_reporter
            AWS responses will be sent to this reporter.

        job_heading_reporter
            Job headings will be sent to this reporter.

        job_data_reporter
            Job data structures will be sent to this reporter.

        job_text_reporter
            Text strings from jobs will be sent to this reporter.

        job_warning_reporter
            Job warnings will be sent to this reporter.

        job_error_reporter
            Job errors will be sent to this reporter.

        stdout_reporter
            Info meant for STDOUT will be sent to this reporter.

        stderr_reporter
            Info meant for STDERR will be sent to this reporter.

    Return:
        A list of security group records from AWS.

    """
    if job_heading_reporter:
        job_heading_reporter(reports, "Fetching auto scaling group by name")
    params = {}
    params["profile"] = profile
    response = launchconfiguration.get(**params)
    utils.check_response_is_ok(
        response,
        reports,
        aws_reporter,
        job_error_reporter,
        stderr_reporter)
    data = utils.get_data_in_response(
        "AutoScalingGroups",
        response,
        reports,
        job_error_reporter,
        stderr_reporter)
    result = None
    if len(data) > 0:
        for record in data:
            if hasattr(record, "get"):
                if record.get("AutoScalingGroupName") == name:
                    result = record
                    break
    if job_data_reporter:
        job_data_reporter(reports, result)
    if stdout_reporter:
        stdout_reporter(reports, result)
    return result
