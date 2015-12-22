# -*- coding: utf-8 -*-

"""The ``main`` module for the ``cli`` package."""

import pprint
import os

import click

from botocore.exceptions import ProfileNotFound

from ..aws import profile


def get_profile(
        profile_name=None,
        access_key_id=None,
        access_key_secret=None):
    if access_key_id and access_key_secret:
        aws_profile = profile.ephemeral(access_key_id, access_key_secret)
    else:
        if not profile_name:
            profile_name = "default"
        try:
            aws_profile = profile.configured(profile_name)
        except ProfileNotFound:
            msg = "No profile '" + str(profile_name) + "'."
            raise click.ClickException(msg)
    return aws_profile


def parse_tags(tags):
    result = []
    if tags:
        for record in tags:
            tag_parts = record.split(":")
            if len(tag_parts) != 2:
                msg = "Bad tag: '" + str(record) + "'. " \
                      + "Must be KEY:VALUE."
                raise click.ClickException(msg)
            key = tag_parts[0].strip()
            value = tag_parts[1].strip()
            if all([key, value]):
                result.append({"Key": key, "Value": value})
            elif not key:
                msg = "Empty tag key: " + str(record)
                raise click.ClickException(msg)
            elif not value:
                msg = "Empty tag value: " + str(record)
                raise click.ClickException(msg)
    return result


def parse_user_data_files(user_data_files):
    result = []
    content_types = [
        "text/x-include-once-url",
        "text/x-include-url",
        "text/cloud-config-archive",
        "text/upstart-job",
        "text/cloud-config",
        "text/part-handler",
        "text/x-shellscript",
        "text/cloud-boothook"
        ]
    if user_data_files:
        for record in user_data_files:
            record_parts = record.split(":")
            if len(record_parts) != 2:
                msg = "'" + str(record) + "' must be FILEPATH:TYPE."
                raise click.ClickException(msg)
            filepath = record_parts[0].strip()
            filetype = record_parts[1].strip()
            if all([filepath, filetype]):
                result.append({"filepath": filepath, "contenttype": filetype})
            elif not filepath:
                msg = "Missing file path: " + str(record)
                raise click.ClickException(msg)
            elif not value:
                msg = "Missing content type: " + str(record)
                raise click.ClickException(msg)
            if not os.path.isfile(filepath):
                msg = "No file '" + str(filepath) + "'."
                raise click.ClickException(msg)
            if filetype not in content_types:
                click.echo("Unknown content type '" + str(filetype) + "'.")
                click.echo("Must be one of:")
                for content_type in content_types:
                    click.echo("- " + str(content_type))
                msg = "Unknown content type for '" + str(filepath) + "'."
                raise click.ClickException(msg)
                
    return result


def parse_listeners(listeners):
    result = []
    allowed_protocols = ["HTTP", "TCP"]
    if listeners:
        for record in listeners:
            listener_parts = record.split(":")
            if len(listener_parts) != 2:
                msg = "Bad listener: '" + str(record) + "'. " \
                      + "Must be PROTOCOL:PORT."
                raise click.ClickException(msg)
            protocol = listener_parts[0].strip().upper()
            port = listener_parts[1].strip()
            if not protocol:
                msg = "Empty protocol value: " + str(record)
                raise click.ClickException(msg)
            elif not port:
                msg = "Empty port value: " + str(record)
                raise click.ClickException(msg)
            if protocol not in allowed_protocols:
                click.echo("Protocol must be one of:")
                click.echo("- HTTP")
                click.echo("- TCP")
                msg = "Unrecognized protocol."
                raise click.ClickException(msg)
            try:
                port = int(port)
            except (TypeError, ValueError):
                msg = "Port must be an integer, not: " + str(port)
                raise click.ClickException(msg)
            if all([protocol, port]):
                result.append({
                    "Protocol": protocol,
                    "LoadBalancerPort": port,
                    "InstanceProtocol": protocol,
                    "InstancePort": port,
                })
    return result
