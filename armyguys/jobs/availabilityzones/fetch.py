# -*- coding: utf-8 -*-

"""Utilities for fetching availaibility zone info."""

from ...aws import availabilityzone

ZONE_BLACKLIST = ["us-east-1a"]


def get_all(
        profile,
        reports=None,
        aws_reporter=None,
        job_heading_reporter=None,
        job_result_reporter=None):
    """Get all availability zones.

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
        A list of availability zone records from AWS.

    """
    if job_heading_reporter:
        job_heading_reporter(reports, "Fetching availability zones")
    params = {}
    params["profile"] = profile
    response = availabilityzone.get(**params)
    if aws_reporter:
        aws_reporter(reports, response)
    data = response.get("AvailabilityZones")
    result = None
    if len(data) > 0:
        result = [x for x in data if x["ZoneName"] not in ZONE_BLACKLIST]
    if job_result_reporter:
        job_result_reporter(reports, result)
    return result
