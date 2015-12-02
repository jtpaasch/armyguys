# -*- coding: utf-8 -*-

"""For creating and managing ECS task definitions."""

from polarexpress.aws.elasticbeanstalk import applicationversion
from polarexpress.aws import profile
from polarexpress.aws import s3

from polarexpress.tasks import utils


def create_application_version(
        aws_profile,
        application,
        name,
        source_bundle):
    """Create a version of an Elastic Beanstalk application.

    Args:

        aws_profile
            A profile to connect to AWS with.

        application
            The name of an application.

        name
            The name/tag you want to give to the version.

    """
    # Figure out the S3 bucket Elastic Beanstalk will use.
    utils.heading("Getting Elastic Beanstalk S3 bucket")
    response = s3.bucket.get_eb_bucket(profile=aws_profile)
    utils.echo_data(response)
    s3bucket = response.get("S3Bucket")
    if s3bucket:
        utils.emphasize("S3 BUCKET: " + str(s3bucket))
    else:
        utils.error("No S3 bucket found in response.")
        utils.exit()

    # Construct the s3 key name.
    utils.heading("Constructing s3 key")
    s3key = "awseb-source-bundle--" + application + "--" + name
    utils.emphasize("S3 KEY: " + str(s3key))

    # Upload a source bundle.
    utils.echo("Uploading source bundle.")
    response = s3.file.create(
        profile=aws_profile,
        filepath=source_bundle,
        s3bucket=s3bucket,
        s3key=s3key)
    utils.echo_data(response)

    utils.heading("Creating application version")
    params = {}
    params["profile"] = aws_profile
    params["application"] = application
    params["name"] = name
    params["s3bucket"] = s3bucket
    params["s3key"] = s3key
    response = applicationversion.create(**params)
    utils.echo_data(response)

    # Exit nicely.
    utils.echo("")
    utils.echo("Done.")


def delete_application_version(
        aws_profile,
        application,
        version):
    """Delete an Elastic Beanstalk application version.

    Args:

        aws_profile
            A profile to connect to AWS with.

        application
            The name of the application the version belongs to.

        version
            The name/tag of the version you want to delete.

    """
    utils.heading("Deleting application version")
    params = {}
    params["profile"] = aws_profile
    params["application"] = application
    params["version"] = version
    response = applicationversion.delete(**params)
    utils.echo_data(response)

    # Exit nicely.
    utils.echo("")
    utils.echo("Done.")


if __name__ == "__main__":
    # Get an AWS profile.
    aws_profile = profile.configured()

    # Get the source bundle from the command line.
    import sys
    source_bundle = sys.argv[1]

    # Set up some parameters.
    application_name = "sally"
    version = "1.0"
    source_bundle = source_bundle

    # Delete the application version.
    params = {}
    params["aws_profile"] = aws_profile
    params["application"] = application_name
    params["version"] = version
    # delete_application_version(**params)
    # utils.exit()    
    
    # Or, create it.
    params = {}
    params["aws_profile"] = aws_profile
    params["application"] = application_name
    params["name"] = version
    params["source_bundle"] = source_bundle
    create_application_version(**params)
