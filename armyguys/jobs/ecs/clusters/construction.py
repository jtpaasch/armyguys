# -*- coding: utf-8 -*-

"""Jobs for creating ECS clusters."""

from ....aws import ecs


def create(
        profile,
        name,
        reports=None,
        aws_reporter=None,
        job_heading_reporter=None,
        job_result_reporter=None):
    """Create an ECS cluster.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name you want to give to the security group.

        vpc
            The ID of a VPC you want to create the group in.

        reports
            A list of reports to send info to.

        aws_reporter
            AWS responses will be sent to this reporter.

        job_heading_reporter
            Job headings will be sent to this reporter.

        job_result_reporter
            Job results will be sent to this reporter.

    Return:
        The data returned by AWS.

    """
    if job_heading_reporter:
        job_heading_reporter(reports, "Creating cluster")
    params = {}
    params["profile"] = profile
    params["name"] = name
    response = ecs.cluster.create(**params)
    if aws_reporter:
        aws_reporter(reports, response)
    result = []
    if hasattr(response, "get"):
        result = response.get("cluster")
    if job_result_reporter:
        job_result_reporter(reports, result)
    return result
