# -*- coding: utf-8 -*-

"""Utilities for fetching VPC info."""

from ...aws import vpc

from ..exceptions import TooManyRecords


def get_all(
        profile,
        reports=None,
        aws_reporter=None,
        job_heading_reporter=None,
        job_result_reporter=None):
    """Get all VPCs.

    Args:

        profile
            A profile to connect to AWS with.

        reports
            A list of reports to send info to.

        aws_reporter
            AWS responses will be sent to this reporter.

        job_heading_reporter
            Job headings will be sent to this reporter.

        job_result_reporter
            Job results will be sent to this reporter.

    Return:
        A list of VPC records from AWS.

    """
    if job_heading_reporter:
        job_heading_reporter(reports, "Fetching VPCs")
    params = {}
    params["profile"] = profile
    response = vpc.get(**params)
    if aws_reporter:
        aws_reporter(reports, response)
    data = response.get("Vpcs")
    result = []
    if len(data) > 0:
        result = data
    if job_result_reporter:
        job_result_reporter(reports, result)
    return result


def get_default_vpc(
        profile,
        reports=None,
        aws_reporter=None,
        job_heading_reporter=None,
        job_result_reporter=None):
    """Get the default VPC.

    Args:

        profile
            A profile to connect to AWS with.

        report
            A list of reports to send info to.

        aws_reporter
            AWS responses will be sent to this reporter.

        job_heading_reporter
            Job headings will be sent to this reporter.

        job_result_reporter
            Job results will be sent to this reporter.

    Return:
        The VPC record returned by AWS, or None if none was found.

    """
    if job_heading_reporter:
        job_heading_reporter(reports, "Fetching default VPC")
    params = {}
    params["profile"] = profile
    params["filters"] = [{"Name": "isDefault", "Values": ["true"]}]
    response = vpc.get(**params)
    if aws_reporter:
        aws_reporter(reports, response)
    data = response.get("Vpcs")
    result = None
    if len(data) > 1:
        msg = "Too many records returned."
        raise TooManyRecords(msg)
    elif len(data) == 1:
        result = data[0]
    if job_result_reporter:
        job_result_reporter(reports, result)
    return result


def get_by_ID(
        profile,
        ID,
        reports=None,
        aws_reporter=None,
        job_heading_reporter=None,
        job_result_reporter=None):
    """Get a VPC by ID.

    Args:

        profile
            A profile to connect to AWS with.

        ID
            The ID of the VPC.

        report
            A list of reports to send info to.

        aws_reporter
            AWS responses will be sent to this reporter.

        job_heading_reporter
            Job headings will be sent to this reporter.

        job_result_reporter
            Job results will be sent to this reporter.

    Return:
        The VPC record returned by AWS, or None if none was found.

    """
    if job_heading_reporter:
        job_heading_reporter(reports, "Fetching VPC by ID")
    params = {}
    params["profile"] = profile
    params["filters"] = [{"Name": "vpc-id", "Values": [ID]}]
    response = vpc.get(**params)
    if aws_reporter:
        aws_reporter(reports, response)
    data = response.get("Vpcs")
    result = None
    if len(data) > 1:
        msg = "Too many records returned."
        raise TooManyRecords(msg)
    elif len(data) == 1:
        result = data[0]
    if job_result_reporter:
        job_result_reporter(reports, result)
    return result
