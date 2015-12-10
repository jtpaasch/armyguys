# -*- coding: utf-8 -*-

"""Utilities for fetching ECS cluster info."""

from ....aws import ecs


def get_all(profile, reports=None, aws_reporter=None):
    """Get all (active) ECS clusters.

    Args:

        profile
            A profile to connect to AWS with.

        reports
            A list of reports to send info to.

        aws_reporter
            AWS responses will be sent to this reporter.

    Return:
        A list of records. returned by AWS.

    """
    params = {}
    params["profile"] = profile
    response = ecs.cluster.get(**params)
    if aws_reporter:
        aws_reporter(reports, response)
    data = response.get("clusters")
    result = []
    if len(data) > 0:
        for record in data:
            status = record.get("status")
            if status == "ACTIVE":
                result.append(record)
    return result


def get_by_name(profile, cluster, reports=None, aws_reporter=None):
    """Get a cluster by name.

    Args:

        profile
            A profile to connect to AWS with.

        cluster
            The name of the cluster you want to fetch.

        reports
            A list of reports to send info to.

        aws_reporter
            AWS responses will be sent to this reporter.

    Return:
        The record returned by AWS, or None if none is found.

    """
    params = {}
    params["profile"] = profile
    response = ecs.cluster.get(**params)
    if aws_reporter:
        aws_reporter(reports, response)
    data = response.get("clusters")
    result = None
    if len(data) > 0:
        for record in data:
            name = record.get("clusterName")
            if name == cluster:
                result = record
                break
    return result
