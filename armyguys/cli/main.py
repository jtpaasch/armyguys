# -*- coding: utf-8 -*-

"""The main ``cli`` module.

This module initializes a plugin-based CLI. The CLI is plugin-based
in the sense that all subcommands are defined in other modules, and
those are loaded into this one. The subcommand modules to load should
be specified in the ``plugins`` dictionary below.

"""

from .plugincli import PluginCli


from .plugins import loadbalancers
from .plugins import securitygroups
from .plugins import subnets
from .plugins import vpcs
from .plugins import zones


plugins = {
    "loadbalancers": loadbalancers,
    "securitygroups": securitygroups,
    "subnets": subnets,
    "vpcs": vpcs,
    "zones": zones,
    }

description = "Manage AWS resources."
cli = PluginCli(name="armyguys", help=description, plugins=plugins)
