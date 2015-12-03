# -*- coding: utf-8 -*-

"""Utilities for working with Elastic Load Balancers."""

from os import path
from . import client as boto3client


def create(
        profile,
        name,
        listeners=None,
        availability_zones=None,
        subnets=None,
        security_groups=None,
        internal=False):
    """Create a load balancer.

    Args:

        profile
            A profile to connect to AWS with.

        name
            The name you want to give to the load balancer..

        listeners
            A list of listener dicts. Each listener dict should
            look like this::

                {
                    "Protocol": "HTTP",
                    "LoadBalancerPort": 80,
                    "InstanceProtocol": "HTTP",
                    "InstancePort": 80,
                    "SSLCertificateId": None
                }

            If no listeners are specified, it will default to HTTP 80->80.

        availability_zones
            A list of availability zones to distribute traffic to. If you
            are launching the load balancer into a VPC, leave this field
            blank and fill in the ``subnets`` parameter below.

        subnets
            A list of subnet IDs, one per availability zone. If you are
            launching into EC2 classic, leave this field blank and fill
            in the ``availability_zones`` parameter above.

        security_groups
            A list of security groups the load balancer should belong to.
            This is only valid in VPCs.

        internal
            Set to ``True`` if the load balancer's DNS should resolve
            to a private IP address. This is only valid in VPCs.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("elb", profile)
    params = {}
    params["LoadBalancerName"] = name
    if not listeners:
        listeners = [{
            "Protocol": "HTTP",
            "LoadBalancerPort": 80,
            "InstanceProtocol": "HTTP",
            "InstancePort": 80,
            }]
    params["Listeners"] = listeners
    if availability_zones:
        params["AvailabilityZones"] = availability_zones
    if subnets:
        params["Subnets"] = subnets
    if security_groups:
        params["SecurityGroups"] = security_groups
    if internal:
        params["Scheme"] = "internal"
    return client.create_load_balancer(**params)


def delete(profile, load_balancer):
    """Delete a load balancer..

    Args:

        profile
            A profile to connect to AWS with.

        load_balancer
            The name of the load balancer you want to delete.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("elb", profile)
    params = {}
    params["LoadBalancerName"] = load_balancer
    return client.delete_load_balancer(**params)


def get(profile, load_balancer=None):
    """Get all load balancers, or a specific one.

    Args:

        profile
            A profile to connect to AWS with.

        load_balancer
            The name of a load balancer to get info for.
            If none is specified, all load balancers are returned.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("elb", profile)
    params = {}
    if load_balancer:
        params["LoadBalancerNames"] = [load_balancer]
    return client.describe_load_balancers(**params)


def tag(profile, load_balancer, key, value):
    """Tag a load balancer.

    Args:

        profile
            A profile to connect to AWS with.

        load_balancer
            The name of the load balancer you want to tag.

        key
            The key/name of the tag.

        value
            The value of the tag.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("elb", profile)
    params = {}
    params["LoadBalancerNames"] = [load_balancer]
    params["Tags"] = [{"Key": key, "Value": value}]
    return client.add_tags(**params)
    

def add_listener(
        profile,
        load_balancer,
        protocol,
        port,
        instance_protocol=None,
        instance_port=None,
        ssl_cert_id=None):
    """Add a listener to a load balancer.

    Args:

        profile
            A profile to connect to AWS with.

        load_balancer
            The name of the load balancer you want to add a listener to.

        protocol
            The protocol you want the load balancer to listen for.

        port
            The port you want the load balancer to listen on.

        instance_protocol
            The protocol to use to forward requests to EC2 instances.
            Defaults to the same as ``protocol``.

        instance_port
            The port to forward requests to EC2 instances on.
            Defaults to the same as ``port``.

        ssl_cert_id
            The ID of an SSL certificate to use.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("elb", profile)
    params = {}
    params["LoadBalancerName"] = load_balancer
    listeners = {}
    if not instance_protocol:
        instance_protocol = protocol
    if not instance_port:
        instance_port = port
    listeners["Protocol"] = protocol
    listeners["LoadBalancerPort"] = port
    listeners["InstanceProtocol"] = instance_protocol
    listeners["InstancePort"] = instance_port
    if ssl_cert_id:
        listeners["SSLCertificateId"] = ssl_cert_id
    params["Listeners"] = [listeners]
    return client.create_load_balancer_listeners(**params)


def remove_listener(profile, load_balancer, port):
    """Remove a listener from a load balancer.

    Args:

        profile
            A profile to connect to AWS with.

        load_balancer
            The name of the load balancer you want to remove a listener from.

        port
            The port you want the load balancer to stop listening on.

    Returns:
        The JSON response returned by boto3.

    """
    client = boto3client.get("elb", profile)
    params = {}
    params["LoadBalancerName"] = load_balancer
    params["LoadBalancerPorts"] = [port]
    return client.delete_load_balancer_listeners(**params)
