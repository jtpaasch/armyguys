# -*- coding: utf-8 -*-

"""Commands for auto scaling group launch configurations."""

import click

from ....jobs.autoscaling import launchconfiguration as launch_config_jobs

from ....jobs.exceptions import BadResponse
from ....jobs.exceptions import ResourceAlreadyExists
from ....jobs.exceptions import ResourceDoesNotExist
from ....jobs.exceptions import ResourceNotCreated
from ....jobs.exceptions import ResourceNotDeleted

from ...reporters import aws as aws_reporter
from ...reporters import console as console_reporter
from ...reporters import jobs as job_reporter
from ...reporters import launchconfigurations as launch_config_reporter
from ...reporters import reporting

from ... import utils


@click.group()
def launchconfigs():
    """Manage launch configurations."""
    pass


@launchconfigs.command(name="list")
@click.option(
    "--report",
    multiple=True,
    default=["quiet"],
    help="Report about records, jobs, AWS.")
@click.option(
    "--profile",
    help="An AWS profile to connect with.")
@click.option(
    "--access-key-id",
    help="An AWS access key ID.")
@click.option(
    "--access-key-secret",
    help="An AWS access key secret.")
def list_launch_configs(
        report=None,
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """List launch configurations."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)
    reports = reporting.parse(report)
    job_reporter.message(reports, "Listing launch configurations...")

    # What reporters should we use?
    reporters = {}
    reporters["reports"] = reports
    reporters["aws_reporter"] = aws_reporter.response
    reporters["job_heading_reporter"] = job_reporter.job
    reporters["job_data_reporter"] = job_reporter.data
    reporters["job_text_reporter"] = job_reporter.message
    reporters["stdout_reporter"] = launch_config_reporter.name
    reporters["stderr_reporter"] = console_reporter.error

    # Fetch the launch configurations.
    try:
        response = launch_config_jobs.fetch.get_all(
            profile=aws_profile,
            **reporters)
    except BadResponse:
        raise click.ClickException("Couldn't understand AWS response.")

    # We're done.
    job_reporter.message(reports, "")
    job_reporter.message(reports, "Done.")


@launchconfigs.command(name="create")
@click.argument("name")
@click.option(
    "--instance-type",
    default="m3.medium",
    help="EC2 instance type.")
@click.option(
    "--security-group",
    multiple=True,
    help="The ID of a security group.")
@click.option(
    "--key-pair",
    help="A key pair for EC2 instances.")
@click.option(
    "--report",
    multiple=True,
    default=["quiet"],
    help="Report about records, jobs, AWS.")
@click.option(
    "--profile",
    help="An AWS profile to connect with.")
@click.option(
    "--access-key-id",
    help="An AWS access key ID.")
@click.option(
    "--access-key-secret",
    help="An AWS access key secret.")
def create_launch_config(
        name,
        instance_type=None,
        security_group=None,
        key_pair=None,
        report=None,
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """Create a launch configurations called NAME."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)
    reports = reporting.parse(report)
    job_reporter.message(reports, "Creating launch configurations...")

    # What reporters should we use?
    reporters = {}
    reporters["reports"] = reports
    reporters["aws_reporter"] = aws_reporter.response
    reporters["job_heading_reporter"] = job_reporter.job
    reporters["job_data_reporter"] = job_reporter.data
    reporters["job_text_reporter"] = job_reporter.message
    reporters["job_warning_reporter"] = job_reporter.warning
    reporters["stderr_reporter"] = console_reporter.error

    # Create the launch configurations.
    try:
        response = launch_config_jobs.construction.create_full(
            profile=aws_profile,
            name=name,
            instance_type=instance_type,
            security_groups=security_group,
            key_pair=key_pair,
            **reporters)
    except (ResourceAlreadyExists, ResourceNotCreated):
        raise click.Abort("")
    except BadResponse:
        raise click.ClickException("Couldn't understand AWS response.")

    # We're done.
    job_reporter.message(reports, "")
    job_reporter.message(reports, "Done.")


@launchconfigs.command(name="delete")
@click.argument("name")
@click.option(
    "--report",
    multiple=True,
    default=["quiet"],
    help="Report about records, jobs, AWS.")
@click.option(
    "--profile",
    help="An AWS profile to connect with.")
@click.option(
    "--access-key-id",
    help="An AWS access key ID.")
@click.option(
    "--access-key-secret",
    help="An AWS access key secret.")
def delete_launch_config(
        name,
        report=None,
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """Delete a launch configurations called NAME."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)
    reports = reporting.parse(report)
    job_reporter.message(reports, "Deleting launch configurations...")

    # What reporters should we use?
    reporters = {}
    reporters["reports"] = reports
    reporters["aws_reporter"] = aws_reporter.response
    reporters["job_heading_reporter"] = job_reporter.job
    reporters["job_data_reporter"] = job_reporter.data
    reporters["job_text_reporter"] = job_reporter.message
    reporters["job_warning_reporter"] = job_reporter.warning
    reporters["stderr_reporter"] = console_reporter.error

    # Delete the launch configuration.
    try:
        response = launch_config_jobs.demolition.delete_full(
            profile=aws_profile,
            name=name,
            **reporters)
    except ResourceDoesNotExist:
        raise click.Abort("")
    except ResourceNotDeleted:
        raise click.ClickException("Couldn't delete launch configuration.")
    except BadResponse:
        raise click.ClickException("Couldn't understand AWS response.")

    # We're done.
    job_reporter.message(reports, "")
    job_reporter.message(reports, "Done.")
