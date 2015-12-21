# -*- coding: utf-8 -*-

"""Job for determining subnets or availability zones in a region."""

from . import availabilityzones as zone_jobs
from . import subnets as subnet_jobs
from . import vpcs as vpc_jobs

from .exceptions import ImproperlyConfigured
from .exceptions import ResourceDoesNotExist


def get_available_sub_regions(
        profile,
        vpc=None,
        subnets=None,
        availability_zones=None):
    """Get availabity zones or subnets you can deploy to.

    You must specify only one of: a VPC, subnets, or availability zones.
    If you specify none of them at all, all subnets for the default VPC
    will be returned (or all availability zones for EC2 classic).
    If you specify a VPC, all subnets for that VPC will be returned.

    Args:

        profile
            A profile to connect to AWS with.

        vpc
            The name or ID of a VPC. If you specify this, all
            subnets in the VPC will be returned.

        subnets
            A list of names (or IDs) of subnets to launch into.
            Leave this blank if you specify a VPC.

        availability_zones
            A list of availability zones to launch into.
            EC2 Classic only.

    Returns:

        A dict with {"availability_zones": [zones], "subnets": [subnet_ids]}.

    """

    # Make sure we only have one of the optional params. There can
    # be zero of them, but there can only be one if any are specified.
    competing_params = [vpc, subnets, availability_zones]
    existing_params = [x for x in competing_params if x]
    if len(existing_params) > 1:
        msg = "Specify only one of: VPC, subnets, or availability zones"
        raise ImproperlyConfigured(msg)
    
    # Check that the availibility_zones exist.
    if availability_zones:
        for zone in availability_zones:
            zone_data = zone_jobs.fetch_by_name(profile, zone)
            if not zone_data:
                msg = "No availability zone '" + str(zone) + "'."
                raise ResourceDoesNotExist(msg)

    # Check tha the subnets exist.
    subnet_ids = []
    if subnets:
        for subnet in subnets:
            subnet_data = subnet_jobs.fetch(profile, subnet)
            if subnet_data:
                subnet_id = subnet_jobs.get_id(subnet_data[0])
                subnet_ids.append(subnet_id)
            else:
                msg = "No subnet '" + str(subnet) + "'."
                raise ResourceDoesNotExist(msg)

    # Check that the VPC exists.
    vpc_id = None
    if vpc:
        vpc_data = vpc_jobs.fetch(profile, vpc)
        if not vpc_data:
            msg = "No VPC '" + str(vpc) + "'."
            raise ResourceDoesNotExist(msg)
        else:
            vpc_id = vpc_jobs.get_id(vpc_data[0])

    # Get the default VPC if needed.
    if not vpc_id:
        vpc_data = vpc_jobs.fetch_default(profile)
        if vpc_data:
            vpc_id = vpc_jobs.get_id(vpc_data[0])

    # If we have no VPC and availability zones, we should
    # get all availability zones.
    if not vpc_id and not availability_zones:
        availability_zones = zone_jobs.fetch_all(profile)
        
    # If we have a VPC and no subnets, we should
    # get all subnets in the VPC.
    if vpc_id and not subnets:
        subnets = subnet_jobs.fetch_by_vpc(profile, vpc_id)
        subnet_ids = [subnet_jobs.get_id(x) for x in subnets]

    # If no availability zones or subnets, we can't proceed.
    required_values = [availability_zones, subnet_ids]
    if not required_values:
        msg = "No availability zones or subnets to launch into."
        raise ImproperlyConfigured(msg)

    # Send back what we have.
    zone_list = availability_zones if availability_zones else None
    subnet_list = subnet_ids if subnet_ids else None
    return {
        "availability_zones": zone_list,
        "subnets": subnet_list,
        }
