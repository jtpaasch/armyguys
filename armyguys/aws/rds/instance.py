# -*- coding: utf-8 -*-

"""Utilities for working with RDS instances."""

from .. import client as boto3client


def get(profile, identifier=None):
    """Get RDS instances.

    Args:

        profile
            A profile to connect to AWS with.

        identifier
            The identifier of an instance.

    Returns:
        The response returned by boto3.

    """
    client = boto3client.get("rds", profile)
    params = {}
    if identifier:
        params["DBInstanceIdentifier"] = identifier
    return client.describe_db_instances(**params)


def delete(profile, identifier, last_snapshot=None, snapshot_identifier=None):
    """Delete an RDS instance.

    Args:

        profile
            A profile to connect to AWS with.

        identifier
            The identifier of the instance you want to delete.

        last_snapshot
            Take a final snapshot before deletion?

        snapshot_identifier
            An identifier for the final snapshot.

    Returns:
        The response returned by boto3.

    """
    client = boto3client.get("rds", profile)
    params = {}
    params["DBInstanceIdentifier"] = identifier
    if last_snapshot is not None:
        params["SkipFinalSnapshot"] = not last_snapshot
    if snapshot_identifier is not None:
        params["FinalDBSnapshotIdentifier"] = snapshot_identifier
    return client.delete_db_instance(**params)


def create(profile, identifier, storage, database_class, engine,
        username, password, db_security_groups=None,
        vpc_security_groups=None, availability_zone=None,
        db_subnet_group=None, parameter_group=None,
        backup_retention=None, port=None, multizone=None,
        engine_version=None, auto_upgrade_minor_version=None,
        iops=None, option_group=None, charset=None, public=None,
        tags=None, encrypted=None):
    """Create an RDS instance.

    Args:

        profile
            A profile to connect to AWS with.

        identifier
            The identifier for the instance.

        storage
            The amount of storage (in gigabytes).

        instance_type
            The database class, e.g., "db.t1.micro."

        engine
            The DB engine, e.g., "MySQL."

        username
            The master username for the DB.

        password
            The master password for the DB.

        db_security_groups
            A list of database security groups. Only for EC2 Classic.

        vpc_security_groups
            A list of VPC security groups. Only for VPCs.

        availability_zone
            The availability zone to create the instance in.
            A random availability zone is chosen by default.
            Do not fill this in if you set ``multizone`` to ``True``.

        db_subnet_group
            The database subnet group. Only for VPCs.

        parameter_group
            The name of a parameter group to use for the DB.

        backup_retention
            The number of days to keep backups.

        port
            The port to use, if different than the DB's default.

        multizone
            Deploy the database into multiple zones?

        engine_version
            The DB engine version. E.g., ``5.7.10`` for MySQL.

        auto_upgrade_minor_version
            Automatically upgrade minor DB engine versions?

        iops
            The amount of provisioned IOPS to give to the instance.

        option_group
            The name of an option group to use for the DB.

        charset
            The character set to use for the database.

        public
            Is the DB publically accessible?

        tags
            A list of {"Key": <key>, "Value": <value>} tags.

        encrypted
            Encrypt the stored data?

    Returns:
        The response returned by boto3.

    """
    client = boto3client.get("rds", profile)
    params = {}
    params["DBInstanceIdentifier"] = identifier
    params["AllocatedStorage"] = storage
    params["DBInstanceClass"] = database_class
    params["Engine"] = engine
    params["MasterUsername"] = username
    params["MasterUserPassword"] = password
    if db_security_groups:
        params["DBSecurityGroups"] = db_security_groups
    if vpc_security_groups:
        params["VpcSecurityGroupIds"] = vpc_security_groups
    if availability_zone:
        params["AvailabilityZone"] = availability_zone
    if db_subnet_group:
        params["DBSubnetGroupName"] = db_subnet_group
    if parameter_group:
        params["DBParameterGroupName"] = parameter_group
    if backup_retention:
        params["BackupRetentionPeriod"] = backup_retention
    if port:
        params["Port"] = port
    if multizone:
        params["MultiAZ"] = multizone
    if engine_version:
        params["EngineVersion"] = engine_version
    if auto_upgrade_minor_version:
        params["AutoMinorVersionUpgrade"] = auto_upgrade_minor_version
    if iops:
        params["Iops"] = iops
    if option_group:
        params["OptionGroupName"] = option_group
    if charset:
        params["CharacterSetName"] = charset
    if public:
        params["PubliclyAccessible"] = public
    if tags:
        params["Tags"] = tags
    if encrypted:
        params["StorageEncrypted"] = encrypted
    return client.create_db_instance(**params)
