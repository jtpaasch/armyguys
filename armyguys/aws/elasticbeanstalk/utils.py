# -*- coding: utf-8 -*-

"""Utilities for working with Amazon's Elastic Beanstalk."""

from .. import client as boto3client


def get_solution_stacks(profile):
    """Get a list of all available solution stacks.

    Args:

        profile
            A profile to connect to AWS with.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("elasticbeanstalk", profile)
    return client.list_available_solution_stacks()


def get_multicontainer_docker_solution_stack(profile):
    """Get the multi-container Docker solution stack.

    This calls ``get_solution_stacks()``, and then steps through the list
    until it finds the multi-container Docker 1.7.1 one.

    Note:
        This method needs to be checked/updated somehow. If Amazon suddenly
        changes their stack to, say, Docker 1.7.2, this method won't work
        anymore, because it's looking for 1.7.1 exactly.

    Args:

        profile
            A profile to connect to AWS with.

    Returns:
        The JSON data for the multi-container Docker 1.7.1 solution stack.

    """
    response = get_solution_stacks(profile)
    stacks = response.get("SolutionStacks")
    match = "Multi-container Docker 1.7.1"
    items_with_match = (x for x in stacks if match in x)
    return next(items_with_match, None)
