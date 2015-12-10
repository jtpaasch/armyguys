# -*- coding: utf-8 -*-

"""Utilities for fetching region info."""

from ...aws import subnet

from ..exceptions import TooManyRecords

from .. import subnets as subnet_jobs
from .. import vpcs as vpc_jobs
from .. import availabilityzones as zone_jobs


def get_all(
        profile,
        vpc=None,
        reports=None,
        aws_reporter=None,
        job_heading_reporter=None,
        job_result_reporter=None):
    """Get all subnet IDs or Availability Zones.

    Args:

        profile
            A profile to connect to AWS with.

        vpc
            The ID of a VPC to get subnets in.

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
    # If no VPC, see if there's a default VPC.
    if not vpc:
        response = vpc_jobs.fetch.get_default_vpc(
            profile=profile,
            reports=reports,
            aws_reporter=aws_reporter,
            job_heading_reporter=job_heading_reporter,
            job_result_reporter=job_result_reporter)
        if response:
            vpc = response["VpcId"]

    # If we have a VPC, get its subnets.
    subnets = None
    if vpc:
        response = subnet_jobs.fetch.get_all_in_vpc(
            profile=profile,
            vpc=vpc,
            reports=reports,
            aws_reporter=aws_reporter,
            job_heading_reporter=job_heading_reporter,
            job_result_reporter=job_result_reporter)
        if response:
            subnets = [x["SubnetId"] for x in response]

    # If we have no VPC, get availability zones instead.
    zones = None
    if not vpc:
        response = zone_jobs.fetch.get_all(
            profile=profile,
            reports=reports,
            aws_reporter=aws_reporter,
            job_heading_reporter=job_heading_reporter,
            job_result_reporter=job_result_reporter)
        if response:
            zones = [x["ZoneName"] for x in response]

    # Send back what we have.
    return {"subnets": subnets, "zones": zones}