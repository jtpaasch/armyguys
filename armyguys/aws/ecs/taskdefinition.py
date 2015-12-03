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


def get(profile, family=None, task_definition=None):
    """Get an ECS task definition.

    If you specify a family, this will return only those task
    definitions that belong to that family. If you specify a
    task definition by its full name (i.e., family:revision),
    this will return only that one task definition. If you
    specify neither a family nor a task definition, this will
    return all task definitions from all families.

    Note that this method returns a list of JSON responses.

    Args:

        profile
            A profile to connect to AWS with.

        family
            A family of task definitions to get.

        task_definition
            A task definition to get, specified by its full name,
            i.e., family:revision.

    Returns:
        A list of data returned by boto3.

    """
    client = boto3client.get("ecs", profile)
    task_definitions = []
    if task_definition:
        task_definitions = [task_definition]
    else:
        params = {}
        if family:
            params["familyPrefix"] = family
        task_definitions_list = client.list_task_definitions(**params)
        task_definitions = task_definitions_list["taskDefinitionArns"]
    results = []
    for task_definition in task_definitions:
        params = {}
        params["taskDefinition"] = task_definition
        response = client.describe_task_definition(**params)
        results.append(response)
    return results
