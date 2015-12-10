# -*- coding: utf-8 -*-

"""Jobs for creating security groups."""

from ...aws import securitygroup


def create(
        profile,
        name,
        vpc=None,
        tags=None,
        reports=None,
        aws_reporter=None,
        job_heading_reporter=None,
        job_result_reporter=None):
    """Create a security group.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name you want to give to the security group.

        vpc
            The ID of a VPC you want to create the group in.

        tags
            A list of {"Name": key, "Value": value} tags.

        reports
            A list of reports to send info to.

        aws_reporter
            AWS responses will be sent to this reporter.

        job_heading_reporter
            Job headings will be sent to this reporter.

        job_result_reporter
            Job results will be sent to this reporter.

    Return:
        The data returned by AWS, or None if none were found.

    """
    if job_heading_reporter:
        job_heading_reporter(reports, "Creating security group")
    has_group_id = False
    params = {}
    params["profile"] = profile
    params["name"] = name
    if vpc:
        params["vpc"] = vpc
    response = securitygroup.create(**params)
    if aws_reporter:
        aws_reporter(reports, response)
    result = None
    if hasattr(response, "get"):
        has_group_id = True
        result = response.get("GroupId")
    if job_result_reporter:
        job_result_reporter(reports, result)

    if tags and has_group_id:
        for record in tags:
            tag(
                profile,
                result,
                record["Name"],
                record["Value"],
                reports,
                aws_reporter,
                job_heading_reporter,
                job_result_reporter)

    return result


def tag(
        profile,
        security_group,
        key,
        value,
        reports=None,
        aws_reporter=None,
        job_heading_reporter=None,
        job_result_reporter=None):
    """Tag a security group.

    Args:

        profile
            A profile to connect to AWS with.

        security_group
            The name of the group you want to tag.

        key
            The key you want to give to the tag.

        value
            The value you want to give to the tag.

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
        job_heading_reporter(reports, "Tagging security group")
    params = {}
    params["profile"] = profile
    params["security_group"] = security_group
    params["key"] = key
    params["value"] = value
    response = securitygroup.tag(**params)
    if aws_reporter:
        aws_reporter(reports, response)
    result = None
    if response:
        result = str(key) + ": " + str(value)
    if job_result_reporter:
        job_result_reporter(reports, result)
    return result
