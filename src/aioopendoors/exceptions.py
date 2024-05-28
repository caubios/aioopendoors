"""Library for exceptions using the Opendoors API."""


class OpendoorsException(Exception):
    """Base class for all client exceptions."""


class ApiException(OpendoorsException):
    """Raised during problems talking to the API."""


class AuthException(OpendoorsException):
    """Raised due to auth problems talking to API."""


class InvalidSyncTokenException(OpendoorsException):
    """Raised when the sync token is invalid."""


class ApiForbiddenException(OpendoorsException):
    """Raised due to permission errors talking to API."""


class ApiUnauthorizedException(OpendoorsException):
    """Raised occasionally, mustn't harm the connection."""


class NoDataAvailableException(OpendoorsException):
    """Raised due updating data, when no data is available."""


class TimeoutException(OpendoorsException):
    """Raised due connecting the websocket."""
