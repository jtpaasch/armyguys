# -*- coding: utf-8 -*-

"""For creating and managing ECS resources."""

import os

from polarexpress.aws import instanceprofile
from polarexpress.aws import policy
from polarexpress.aws import profile
from polarexpress.aws import role

from polarexpress.tasks import utils


def create_instance_profile(
        aws_profile,
        instance_profile_name,
        policy_contents=None,
        policy_file=None):
    """Create an instance profile."""
    utils.heading("Creating role for EC2.")
    instance_profile_role = instance_profile_name
    utils.emphasize("ROLE NAME: " + str(instance_profile_role))
    instance_profile_policy = instance_profile_name + "--policy"
    utils.emphasize("POLICY NAME: " + str(instance_profile_policy))
    utils.emphasize("INSTANCE PROFILE NAME: " + str(instance_profile_name))
    response = role.create(
        profile=aws_profile,
        name=instance_profile_role,
        contents={
            "Version": "2012-10-17",
            "Statement": {
                "Effect": "Allow",
                "Principal": {
                    "Service": "ec2.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        })
    utils.echo_data(response)

    # Make sure we have a policy.
    utils.heading("Checking contents or file")
    if not policy_contents and not policy_file:
        utils.error("No policy. Need ``policy_contents`` or a ``policy_file``.")
        utils.exit()
    elif policy_contents and policy_file:
        utils.error("Pick either ``policy_contents`` or ``policy_file``.")
        utils.exit()
    utils.echo("Policy contents or file provided.")

    # If it's a file reference, load its contents.
    if policy_file:
        utils.heading("Loading policy file contents")
        norm_path = os.path.normpath(policy_file)
        norm_path = norm_path.rstrip(os.path.sep)
        with open(norm_path, "rb") as f:
            raw_contents = f.read()
            policy_contents = raw_contents.decode("utf-8")
        utils.echo_data(policy_contents)

    # Create the policy.
    utils.heading("Creating policy")
    response = policy.create(
        profile=aws_profile,
        name=instance_profile_policy,
        contents=policy_contents)
    utils.echo_data(response)
    policy_arn = response["Policy"]["Arn"]
    utils.emphasize("POLICY ARN: " + str(policy_arn))
        
    # Attach the policy to the role.
    utils.heading("Attaching policy to role")
    response = role.attach_policy(
        profile=aws_profile,
        role=instance_profile_role,
        policy=policy_arn)
    utils.echo_data(response)

    # Create an instance profile.
    utils.heading("Creating instance profile")
    response = instanceprofile.create(
        profile=aws_profile,
        name=instance_profile_name)
    utils.echo_data(response)
    profile_arn = response["InstanceProfile"]["Arn"]
    utils.emphasize("INSTANCE PROFILE ARN: " + str(profile_arn))

    # Attach the role to the instance profile.
    utils.heading("Attaching role to instance profile")
    response = instanceprofile.add_role(
        profile=aws_profile,
        instance_profile=instance_profile_name,
        role=instance_profile_role)
    utils.echo_data(response)

    # Exit nicely.
    utils.echo("Done.")


if __name__ == "__main__":
    # Get an AWS profile.
    aws_profile = profile.configured()

    # Create a policy.
    ecs_policy_contents = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "ec2:Describe*",
                    "elasticloadbalancing:*",
                    "ecs:*",
                    "iam:ListInstanceProfiles",
                    "iam:ListRoles",
                    "iam:PassRole",
                    "s3:Get*",
                    "s3:List*"
                ],
                "Resource": "*"
            }
        ]
    }

    # Now create the instance profile.
    create_instance_profile(
        aws_profile=aws_profile,
        instance_profile_name="ecs-instance-profile",
        policy_contents=ecs_policy_contents)
