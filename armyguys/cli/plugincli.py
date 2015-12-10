# -*- coding: utf-8 -*-

"""A plugin-based ``click`` CLI.

This subclass simply loads the subcommands from plugins passed to
the constructor. Each module is just a regular old python module
which defines some ``click`` command (or command group).

"""

import click


class PluginCli(click.MultiCommand):
    """A ``click`` CLI that loads its subcommands from plugins.

    The plugins are passed to the constructor as a parameter.

    """

    plugins = {}
    """A dictionary of plugins to load.

    Each entry's key should be the name of the subcommand,
    and the value should be a module that implements the subcommand.
    The module must implement the command or else an error is raised.

    """

    def __init__(self, plugins, *args, **kwargs):
        """Store the ``plugins`` dict, then invokes the parent."""
        self.plugins = plugins
        return super(PluginCli, self).__init__(*args, **kwargs)

    def list_commands(self, ctx):
        """Return a list of all subcommand names (the plugin names)."""
        list_of_names = []
        for key in self.plugins:
            list_of_names.append(key)
        list_of_names.sort()
        return list_of_names

    def get_command(self, ctx, name):
        """Load the command from the plugin.

        If there is no such plugin, an exception is raised.

        If the plugin module does not implement the command,
        an exception is raised.

        """
        try:
            plugin = self.plugins[name]
        except KeyError:
            ctx.fail("No such command '" + str(name) + "'.")
        try:
            command = getattr(plugin, name)
        except AttributeError:
            message = "Improperly configured plugin.\n"
            message += "No command called `" + str(name) + "` "
            message += "is defined in the module "
            message += "`" + str(plugin.__name__) + "`.\n"
            ctx.fail(message)
        return command
