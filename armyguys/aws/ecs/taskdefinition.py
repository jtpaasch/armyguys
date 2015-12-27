# -*- coding: utf-8 -*-

"""Utilities for working with ECS task definitions."""

import json
import os
from .. import client as boto3client


def create(profile, contents=None, filepath=None):
    """Upload a task definition to ECS.

    Args:

        profile
            A profile to connect to AWS with.

        contents
            The contents of the task definition you want to upload.
            You must specify this OR a filepath.

        filepath
            The path to a task definition *.json file you want to upload.
            You must specify this OR a filepath.

    Returns:
        The data returned by boto3.

    """
    if contents:
        data = contents
    elif filepath:
        norm_path = os.path.normpath(filepath)
        normpath = norm_path.rstrip(os.path.sep)
        with open(filepath) as f:
            data = json.load(f)
    client = boto3client.get("ecs", profile)
    params = {}
    params["family"] = data.get("family")
    params["containerDefinitions"] = data.get("containerDefinitions")
    params["volumes"] = data.get("volumes")
    if params["volumes"] is None:
        params["volumes"] = []
    return client.register_task_definition(**params)


def delete(profile, name):
    """Delete an ECS task definition.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The full name, i.e., family:revision.

    Returns:
        The data returned by boto3.

    """
    client = boto3client.get("ecs", profile)
    params = {}
    params["taskDefinition"] = name
    return client.deregister_task_definition(**params)


def get_arns(profile, family=None):
    """Get ECS task definition arns.

    Args:

        profile
            A profile to connect to AWS with.

        family
            A family of task definitions to get.

    Returns:
        A list of data returned by boto3.

    """
    client = boto3client.get("ecs", profile)
    params = {}
    if family:
        params["familyPrefix"] = family
    return client.list_task_definitions(**params)


def get_families(profile, family=None):
    """Get ECS task definition families.

    Args:

        profile
            A profile to connect to AWS with.

        family
            A family of task definitions to get.

    Returns:
        A list of data returned by boto3.

    """
    client = boto3client.get("ecs", profile)
    params = {}
    if family:
        params["familyPrefix"] = family
    return client.list_task_definition_families(**params)


def get(profile, task_definition):
    """Get an ECS task definition.

    Args:

        profile
            A profile to connect to AWS with.

        task_definition
            A task definition to get, specified by its full name,
            i.e., family:revision.

    Returns:
        The data returned by boto3.

    """
    client = boto3client.get("ecs", profile)
    params = {}
    params["taskDefinition"] = task_definition
    return client.describe_task_definition(**params)
