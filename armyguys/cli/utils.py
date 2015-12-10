# -*- coding: utf-8 -*-

"""The ``main`` module for the ``cli`` package."""

import pprint

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


def parse_tags(tag):
    tags = []
    if tag:
        for record in tag:
            tag_parts = record.split(":")
            if len(tag_parts) != 2:
                msg = "Bad tag: '" + str(record) + "'. " \
                      + "Must be KEY:VALUE."
                raise click.ClickException(msg)
            key = tag_parts[0].strip()
            value = tag_parts[1].strip()
            if all([key, value]):
                tags.append({"Name": key, "Value": value})
            elif not key:
                msg = "Empty tag key: " + str(record)
                raise click.ClickException(msg)
            elif not value:
                msg = "Empty tag value: " + str(record)
                raise click.ClickException(msg)
    return tags
