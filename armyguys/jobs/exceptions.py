# -*- coding: utf-8 -*-

"""Custom exceptions for jobs."""


class AwsError(Exception):
    """Raise when AWS raises an error we don't expect."""
    pass


class FileDoesNotExist(Exception):
    """Raise when a file doesn't exist on a filesystem."""
    pass

class MissingKey(Exception):
    """Raise when expected key is missing in an AWS response."""
    pass


class Non200Response(Exception):
    """Raise when AWS returns a non-200 response."""
    pass


class PermissionDenied(Exception):
    """Raise when the user lacks permission/authorization."""
    pass


class ResourceAlreadyExists(Exception):
    """Raise when a resource already exists."""
    pass


class ResourceDoesNotExist(Exception):
    """Raise when a resource does not exist."""
    pass


class ResourceHasDependency(Exception):
    """Raise when a resource is dependent on another resource."""
    pass


class ResourceNotCreated(Exception):
    """Raise when a resource failed to get created."""
    pass


class ResourceNotDeleted(Exception):
    """Raise when a resource failed to get deleted."""
    pass


class TooManyRecords(Exception):
    """Raise when too many records are returned."""
    pass


class WaitTimedOut(Exception):
    """Raise when a poll/wait timed out."""
    pass
