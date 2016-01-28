# -*- coding: utf-8 -*-

"""Utilities for working with IAM server certificates."""

from .. import client as boto3client


def create(profile, name, certificate_contents, key_contents):
    """Create a VPC:.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name you want to give to the certificate.

        certificate_contents
            The body of the certificate.

        key_contents
            The body of the certificate key.

    Returns:
        The data returned by boto3.

    """
    client = boto3client.get("iam", profile)
    params = {}
    params["ServerCertificateName"] = name
    params["CertificateBody"] = certificate_contents
    params["PrivateKey"] = key_contents
    return client.upload_server_certificate(**params)


def get(profile):
    """Get a list of all server certificates.

    Args:

        profile
            A profile to connect to AWS with.

    Returns:
        The data returned by boto3.

    """
    client = boto3client.get("iam", profile)
    params = {}
    return client.list_server_certificates(**params)
