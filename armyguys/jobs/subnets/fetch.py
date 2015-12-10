# -*- coding: utf-8 -*-

"""Utilities for fetching subnet info."""

from ...aws import subnet

from ..exceptions import TooManyRecords


def get_all(
        profile,
        reports=None,
        aws_reporter=None,
        job_heading_reporter=None,
        job_result_reporter=None):
    """Get all subnets.

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
        A list of subnet records from AWS.

    """
    if job_heading_reporter:
        job_heading_reporter(reports, "Fetching subnets")
    params = {}
    params["profile"] = profile
    response = subnet.get(**params)
    if aws_reporter:
        aws_reporter(reports, response)
    data = response.get("Subnets")
    result = []
    if len(data) > 0:
        result = data
    if job_result_reporter:
        job_result_reporter(reports, result)
    return result


def get_all_in_vpc(
        profile,
        vpc,
        reports=None,
        aws_reporter=None,
        job_heading_reporter=None,
        job_result_reporter=None):
    """Get all subnets in a VPC.

    Args:

        profile
            A profile to connect to AWS with.

        vpc
            The IF of the VPC to find subnets in.

        report
            A list of reports to send info to.

        aws_reporter
            AWS responses will be sent to this reporter.

        job_heading_reporter
            Job headings will be sent to this reporter.

        job_result_reporter
            Job results will be sent to this reporter.

    Return:
        The subnet records returned by AWS, or None if none were found.

    """
    if job_heading_reporter:
        job_heading_reporter(reports, "Fetching subnets in VPC")
    params = {}
    params["profile"] = profile
    params["filters"] = [{"Name": "vpc-id", "Values": [vpc]}]
    response = subnet.get(**params)
    if aws_reporter:
        aws_reporter(reports, response)
    data = response.get("Subnets")
    result = None
    if len(data) > 0:
        result = data
    if job_result_reporter:
        job_result_reporter(reports, result)
    return result
