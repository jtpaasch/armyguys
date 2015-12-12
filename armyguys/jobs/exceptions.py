# -*- coding: utf-8 -*-

"""Custom exceptions for jobs."""


class AwsError(Exception):
    """Raise when AWS raises an error we don't expect."""
    pass


class MissingKey(Exception):
    """Raise when expected key is missing in an AWS response."""


class Non200Response(Exception):
    """Raise when AWS returns a non-200 response."""


class PermissionDenied(Exception):
    """Raise when the user lacks permission/authorization."""
    pass


class ResourceAlreadyExists(Exception):
    """Raise when a resource already exists."""
    pass


class ResourceDoesNotExist(Exception):
    """Raise when a resource does not exist."""
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
