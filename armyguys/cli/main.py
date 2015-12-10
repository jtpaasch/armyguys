# -*- coding: utf-8 -*-

"""The main ``cli`` module.

This module initializes a plugin-based CLI. The CLI is plugin-based
in the sense that all subcommands are defined in other modules, and
those are loaded into this one. The subcommand modules to load
should be specified in the ``plugins`` dictionary below.

"""

from .plugincli import PluginCli


from .commands.ecs import clusters
from .commands.autoscaling import launchconfigs
from .commands.autoscaling import scalinggroups
from .commands import loadbalancers
from .commands import securitygroups
from .commands import subnets
from .commands import vpcs
from .commands import zones


plugins = {
    "clusters": clusters,
    "launchconfigs": launchconfigs,
    "loadbalancers": loadbalancers,
    "scalinggroups": scalinggroups,
    "securitygroups": securitygroups,
    "subnets": subnets,
    "vpcs": vpcs,
    "zones": zones,
    }

description = "Manage AWS resources."
cli = PluginCli(name="armyguys", help=description, plugins=plugins)
