# -*- coding: utf-8 -*-

"""Jobs for fetching security group data."""

from ...aws import securitygroup

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
        stderr_reporter=None)
    """Get all security groups.

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
        job_heading_reporter(reports, "Fetching security groups")
    params = {}
    params["profile"] = profile
    response = securitygroup.get(**params)
    utils.check_response_is_ok(
        response,
        reports,
        aws_reporter,
        job_error_reporter,
        stderr_reporter)
    data = utils.get_data_in_response(
        "SecurityGroups",
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


def get_all_in_vpc(
        profile,
        vpc,
        reports=None,
        aws_reporter=None,
        job_heading_reporter=None,
        job_result_reporter=None):
    """Get all security groups in a VPC.

    Args:

        profile
            A profile to connect to AWS with.

        vpc
            The ID of a VPC to find security groups in.

        reports
            A list of reports to send info to.

        aws_reporter
            AWS responses will be sent to this reporter.

        job_heading_reporter
            Job headings will be sent to this reporter.

        job_result_reporter
            Job results will be sent to this reporter.

    Return:
        A list of security group records from AWS.

    """
    if job_heading_reporter:
        job_heading_reporter(reports, "Fetching security groups in VPC")
    params = {}
    params["profile"] = profile
    params["filters"] = [{"Name": "vpc-id", "Values": [vpc]}]
    response = securitygroup.get(**params)
    if aws_reporter:
        aws_reporter(reports, response)
    data = response.get("SecurityGroups")
    result = None
    if len(data) > 0:
        result = data
    if job_result_reporter:
        job_result_reporter(reports, result)
    return result


def get_by_name(
        profile,
        name,
        reports=None,
        aws_reporter=None,
        job_heading_reporter=None,
        job_result_reporter=None):
    """Get a security group by name.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name of the security group.

        reports
            A list of reports to send info to.

        aws_reporter
            AWS responses will be sent to this reporter.

        job_heading_reporter
            Job headings will be sent to this reporter.

        job_result_reporter
            Job results will be sent to this reporter.

    Return:
        The security group record returned by AWS, or None if none was found.

    """
    if job_heading_reporter:
        job_heading_reporter(reports, "Fetching security group by name")
    params = {}
    params["profile"] = profile
    params["filters"] = [{"Name": "group-name", "Values": [name]}]
    response = securitygroup.get(**params)
    if aws_reporter:
        aws_reporter(reports, response)
    data = response.get("SecurityGroups")
    result = None
    if len(data) > 1:
        msg = "Too many records returned."
        raise TooManyRecords(msg)
    elif len(data) == 1:
        result = data[0]
    if job_result_reporter:
        job_result_reporter(reports, result)
    return result
