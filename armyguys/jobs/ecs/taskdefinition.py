# -*- coding: utf-8 -*-

"""For creating and managing ECS task definitions."""

from ...aws.ecs import taskdefinition
from ...aws import profile

from ...jobs import utils


def create_task_definition(
        aws_profile,
        contents=None,
        filepath=None):
    """Create an ECS task definition."""
    utils.heading("Uploading task definition")
    params = {}
    params["profile"] = aws_profile
    if contents:
        params["contents"] = contents
        utils.emphasize("CONTENTS:")
        utils.echo_data(contents)
    elif filepath:
        params["filepath"] = filepath
        utils.emphasize("FILEPATH: " + str(filepath))
    response = taskdefinition.create(**params)
    utils.echo("")
    utils.emphasize("RESPONSE:")
    utils.echo_data(response)

    # Exit nicely.
    utils.echo("Done.")


if __name__ == "__main__":
    # Get an AWS profile.
    aws_profile = profile.configured()

    # A task definition.
    task_definition = {
        "family": "simpleton",
        "containerDefinitions": [
            {
                "name": "simpleton",
                "image": "jtpaasch/simpleton:latest",
                "memory": 100,
                "portMappings": [
                    {
                        "containerPort": 80,
                        "hostPort": 80
                    }
                ]
            }
        ]
    }

    # Upload it.
    create_task_definition(
        aws_profile=aws_profile,
        contents=task_definition)
