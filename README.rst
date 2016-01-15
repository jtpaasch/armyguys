Army Guys
=========

Run Docker containers in Amazon's cloud.

This is in active development, but here's the basic rundown.


Install
-------

Pip install from the repo (preferably in a virtual environment):

    pip install git+https://github.com/jtpaasch/armyguys.git#egg=armyguys

Then checkout the help:

    armyguys


Make Sure You Can Connect to AWS
--------------------------------

From the command line, type this::

    armyguys zones list

If all is working, that should list all availability zones in your region.

If you get a permissions error, check out the *Authenticating* section below.


Clusters
--------

ECS clusters are managed with the ``armyguys clusters`` command::

    armyguys clusters --help

To see all your clusters, use ``list``::

    armyugys clusters list

To create a cluster named "my-app-cluster", use ``create my-app-cluster``::

    armyguys clusters create my-app-cluster

To delete that cluster, use ``delete my-app-cluster``::

    armyguys clusters delete my-app-cluster


Task Definitions
----------------

Task definitions are managed with the ``armyguys taskdefinitions`` command::

    armyguys taskdefinitions --help

To see all task definitions, use ``list``::

    armyguys taskdefinitions list

To create a task definition, use ``create`` and point it to the file on
your machine::

    armyguys taskdefinitions create --filepath ~/taskdefs/my-app-task-def.json

That will create version 1, i.e., ``my-app-task-def:1``.
    
To delete it, use ``delete my-app-task-def:1``::

    armyguys taskdefinitions delete my-app-task-def:1


Tasks
-----

ECS tasks are managed with the ``armyguys tasks`` command::

    armyguys tasks --help

To see all tasks in a cluster, use ``list CLUSTER``, e.g.,::

    armyguys tasks list my-app-cluster

To create a task called "my-app-task" in a cluster, use
``create my-app-task`` and specify the cluster and task definition::

    armyguys tasks create my-app-task \
        --cluster my-app-cluster \
        --task-definition my-app-task-def:1

To delete that task, use ``delete my-app-task`` and specify
the cluster::

    armyguys tasks delete my-app-task --cluster my-app-cluster


Services
--------

ECS services are managed with the ``armyguys services`` command::

    armyguys services --help

To see all services in a cluster, use ``list CLUSTER``, e.g.,::

    armyguys services list my-app-cluster

To create a service called "my-app-service" in a cluster, use
``create my-app-service`` and specify the cluster and task definition::

    armyguys services create my-app-service \
        --cluster my-app-cluster \
        --task-definition my-app-task-def:1

To delete that service, use ``delete my-app-service`` and specify
the cluster::

    armyguys services delete my-app-task --cluster my-app-cluster


Authenticating
--------------

Most ``armyguys`` commands need to connect to AWS. For that, ``armyguys``
needs credentials.

By default, ``armyguys`` will use the default profile it finds on your
machine in the file ``~/.aws/credentials``.

If you have that file with a ``[default]`` section in it, then
``armyguys`` should just work.

Try it out. List all availability zones for your region::

    armyguys zones list

If you have other profiles in your ``~/.aws/credentials`` file, you can
specify which one you want to use with the ``--profile`` parameter.

For instance, suppose you have another section in ``~/.aws/credentials``
called ``[foo]``. You can tell ``armyguys`` to use that profile
like this::

    armyguys zones list --profile foo

If you don't want to rely on the ``~/.aws/credentials`` file at all, you
can use the ``--access-key-id`` and ``access-key-secret`` parameters to
specify your AWS access keys, like this::

    armyguys zones list \
        --access-key-id ACCESS-KEY \
        --access-key-secret KEY-SECRET


Help and Other Commands
-----------------------

To see the help, just type ``armyguys`` from the command line::

    armyguys

You can also use the ``--help`` flag after any command or subcommand.
For instance::

    armyguys tasks create --help

