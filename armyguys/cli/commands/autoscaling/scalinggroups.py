# -*- coding: utf-8 -*-

"""Commands for auto scaling group launch configurations."""

import click

from ....jobs.autoscaling import autoscalinggroup as scaling_group_jobs

from ....jobs.exceptions import BadResponse
from ....jobs.exceptions import MissingDataInResponse
from ....jobs.exceptions import Non200Response
from ....jobs.exceptions import ResourceAlreadyExists
from ....jobs.exceptions import ResourceNotCreated

from ...reporters import autoscalinggroups as scalinggroup_reporter
from ...reporters import aws as aws_reporter
from ...reporters import console as console_reporter
from ...reporters import jobs as job_reporter
from ...reporters import reporting

from ... import utils


@click.group()
def scalinggroups():
    """Manage auto scaling groups."""
    pass


@scalinggroups.command(name="list")
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
def list_scaling_groups(
        report=None,
        profile=None,
        access_key_id=None,
        access_key_secret=None):
    """List auto scaling groups."""
    aws_profile = utils.get_profile(profile, access_key_id, access_key_secret)
    reports = reporting.parse(report)
    job_reporter.message(reports, "Listing auto scaling groups...")

    # What reporters should we use?
    reporters = {}
    reporters["reports"] = reports
    reporters["aws_reporter"] = aws_reporter.response
    reporters["job_heading_reporter"] = job_reporter.job
    reporters["job_data_reporter"] = job_reporter.data
    reporters["job_text_reporter"] = job_reporter.message
    reporters["stdout_reporter"] = scalinggroup_reporter.name
    reporters["stderr_reporter"] = console_reporter.error

    # Fetch the auto scaling groups.
    try:
        response = scaling_group_jobs.fetch.get_all(
            profile=aws_profile,
            **reporters)
    except (BadResponse, MissingDataInResponse, Non200Response):
        raise click.ClickException("Couldn't handle response.")

    # We're done.
    job_reporter.message(reports, "")
    job_reporter.message(reports, "Done.")


@scalinggroups.command(name="create")
@click.argument("name")
@click.option(
    "--instance-type",
    default="m3.medium",
    help="EC2 instance type.")
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
def create_scaling_group(
        name,
        instance_type=None,
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
    '''
    try:
        response = launch_config_jobs.construction.create_full(
            profile=aws_profile,
            name=name,
            instance_type=instance_type,
            **reporters)
    except (ResourceAlreadyExists, ResourceNotCreated):
        raise click.Abort("")
    except BadResponse:
        raise click.ClickException("Couldn't understand AWS response.")
    '''

    # We're done.
    job_reporter.message(reports, "")
    job_reporter.message(reports, "Done.")
