# -*- coding: utf-8 -*-

"""For creating and managing ECS tasks."""

from os import path

from ...aws import autoscaling
from ...aws import loadbalancer
from ...aws import profile

from ...jobs import utils


def get_autoscalinggroup_name(cluster_name):
    """Get the name for a cluster's auto scaling group.

    Args:

        cluster_name
            The name of the cluster.

    Returns:
        The cluster's auto scaling group name (a string).

    """
    return cluster_name + "--autoscaling-group"


def get_autoscalinggroup_info(aws_profile, autoscalinggroup_name):
    """Get info about an autoscaling group.

    Args:

        aws_profile
            A profile to connect to AWS with.

        autoscalinggroup_name
            The name of the autoscaling group to fetch info about.

    Returns:
        The JSON response returned by boto3.

    """
    response = autoscaling.autoscalinggroup.get(aws_profile, autoscalinggroup_name)
    as_groups = response["AutoScalingGroups"]
    result = []
    if as_groups:
        result = [x for x in as_groups
                  if x["AutoScalingGroupName"] == autoscalinggroup_name]
    return result


def get_loadbalancer_info(aws_profile, loadbalancer_name):
    """Get info about a load balancer.

    Args:

        aws_profile
            A profile to connect to AWS with.

        loadbalancer_name
            The name of the load balancer to fetch info about.

    Returns:
        The JSON response returned by boto3.

    """
    response = loadbalancer.get(aws_profile, loadbalancer_name)
    load_balancers = response["LoadBalancerDescriptions"]
    result = []
    if load_balancers:
        result = [x for x in load_balancers
                  if x["LoadBalancerName"] == loadbalancer_name]
    return result


def attach_loadbalancer(
        aws_profile,
        cluster,
        load_balancer):
    """Attach a load balancer to a cluster.

    Args:

        aws_profile
            A profile to connect to AWS with.

        cluster
            The name of a cluster to attach a load balancer to.

        load_balancer
            The name of the load balancer you want to attach.

    """
    autoscalinggroup_name = get_autoscalinggroup_name(cluster)

    # Make sure the auto scaling group exists.
    utils.heading("Checking that the autoscaling group exists")
    response = get_autoscalinggroup_info(
        aws_profile,
        autoscalinggroup_name)
    if response:
        utils.echo_data(response)
        msg = "Ok. Autoscaling group '" + autoscalinggroup_name + "' found."
        utils.emphasize(msg)
    else:
        msg = "No such autoscaling group '" + autoscalinggroup_name + "'."
        utils.error(msg)
        utils.exit()

    # Make sure the load balancer exists.
    utils.heading("Checking that the load balancer exists")
    response = get_loadbalancer_info(
        aws_profile,
        load_balancer)
    if response:
        utils.echo_data(response)
        utils.emphasize("Ok. Load balancer '" + load_balancer + "' found.")
    else:
        msg = "No such load balancer '" + load_balancer + "'."
        utils.error(msg)
        utils.exit()

    # Attach the load balancer to the auto scaling group.
    utils.heading("Attaching the load balancer to the autoscaling group")
    response = autoscaling.autoscalinggroup.attach_load_balancer(
        profile=aws_profile,
        autoscaling_group=autoscalinggroup_name,
        load_balancer=load_balancer)
    if response:
        utils.echo_data(response)
        msg = "Load balancer '" + load_balancer \
              + "' attached to '" \
              + autoscalinggroup_name + "'."
        utils.emphasize(msg)
    else:
        msg = "Unexpected data returned by 'attach load balancer' request."
        utils.error(msg)
        utils.exit()

    # Exit nicely.
    utils.echo("")
    utils.echo("Done.")


def detach_loadbalancer(
        aws_profile,
        cluster,
        load_balancer):
    """Detach a load balancer from a cluster.

    Args:

        aws_profile
            A profile to connect to AWS with.

        cluster
            The name of a cluster to detach a load balancer from.

        load_balancer
            The name of the load balancer you want to detach.

    """
    autoscalinggroup_name = get_autoscalinggroup_name(cluster)

    # Make sure the auto scaling group exists.
    utils.heading("Checking that the autoscaling group exists")
    response = get_autoscalinggroup_info(
        aws_profile,
        autoscalinggroup_name)
    if response:
        utils.echo_data(response)
        msg = "Ok. Autoscaling group '" + autoscalinggroup_name + "' found."
        utils.emphasize(msg)
    else:
        msg = "No such autoscaling group '" + autoscalinggroup_name + "'."
        utils.error(msg)
        utils.exit()

    # Make sure the load balancer exists.
    utils.heading("Checking that the load balancer exists")
    response = get_loadbalancer_info(
        aws_profile,
        load_balancer)
    if response:
        utils.echo_data(response)
        utils.emphasize("Ok. Load balancer '" + load_balancer + "' found.")
    else:
        msg = "No such load balancer '" + load_balancer + "'."
        utils.error(msg)
        utils.exit()

    # Detach the load balancer from the auto scaling group.
    utils.heading("Detaching the load balancer from the autoscaling group")
    response = autoscaling.autoscalinggroup.detach_load_balancer(
        profile=aws_profile,
        autoscaling_group=autoscalinggroup_name,
        load_balancer=load_balancer)
    if response:
        utils.echo_data(response)
        msg = "Load balancer '" + load_balancer \
              + "' detached from '" \
              + autoscalinggroup_name + "'."
        utils.emphasize(msg)
    else:
        msg = "Unexpected data returned by 'detach load balancer' request."
        utils.error(msg)
        utils.exit()

    # Exit nicely.
    utils.echo("")
    utils.echo("Done.")


if __name__ == "__main__":
    # Get an AWS profile.
    aws_profile = profile.configured()

    # Define some parameters.
    cluster="joe-cluster"
    load_balancer="joe-loadbalancer"

    # Set up the parameters.
    params = {}
    params["aws_profile"] = aws_profile
    params["cluster"] = cluster
    params["load_balancer"] = load_balancer

    # Detach the load balancer.
    # detach_loadbalancer(**params)
    # utils.exit()
    
    # Attach the load balancer.
    attach_loadbalancer(**params)
