# -*- coding: utf-8 -*-

"""Custom exceptions for jobs."""


class BadResponse(Exception):
    """Raise when AWS returns a response we can't parse."""
    pass


class MissingDataInResponse(Exception):
    """Raise when expected data is missing in a response."""


class Non200Response(Exception):
    """Raise when AWS returns a non-200 response."""


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
