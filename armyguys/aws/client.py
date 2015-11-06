# -*- coding: utf-8 -*-

"""Utilities for getting boto3 clients for AWS services."""

import boto3


def get(service, session=None):
    """Get a boto3 client for an AWS service.

    Args:

        service
            The name of the AWS service you want a client for.

        session
            A boto3 session to use. The provided session may have
            credentials and a region configured for it. If no session
            is specified here, a default session will be created.

    Returns:
        An instance of a boto3 client for the requested service.

    """
    if not session:
        session = boto3.Session()
    return session.client(service)
