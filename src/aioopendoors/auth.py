"""Module for AbstractAuth for Opendoors."""

import logging
from abc import ABC, abstractmethod
from http import HTTPStatus
from typing import Any

from aiohttp import ClientError, ClientResponse, ClientResponseError, ClientSession

from .exceptions import (
    ApiException,
    ApiForbiddenException,
    ApiUnauthorizedException,
    AuthException,
)

ERROR = "error"
STATUS = "status"
MESSAGE = "message"

_LOGGER = logging.getLogger(__name__)


class AbstractAuth(ABC):
    """Abstract class to make authenticated requests."""

    def __init__(self, websession: ClientSession, host: str) -> None:
        """Initialize the auth."""
        self.websession = websession
        self._host = host

    @abstractmethod
    async def async_get_access_token(self) -> str:
        """Return a valid access token."""

    async def request(self, method: str, url: str, **kwargs) -> ClientResponse:
        """Make a request."""
        access_token = await self._async_get_access_token()

        return await self.websession.request(
            method,
            f"{self._host}/{url}&oauth2={access_token}",
            **kwargs,
        )

    async def get(self, url: str, **kwargs) -> ClientResponse:
        """Make a get request."""
        try:
            resp = await self.request("get", url, **kwargs)
        except ClientError as err:
            raise ApiException(f"Error connecting to API: {err}") from err
        return await AbstractAuth._raise_for_status(resp)

    async def get_json(self, url: str, **kwargs) -> dict[str, Any]:
        """Make a get request and return json response."""
        resp = await self.get(url, **kwargs)
        try:
            result = await resp.json(encoding="UTF-8")
        except ClientError as err:
            raise ApiException("Server returned malformed response") from err
        if not isinstance(result, dict):
            raise ApiException(f"Server return malformed response: {result}")
        _LOGGER.debug("get_json(%s,...) : response=%s", url, result)
        return result

    async def _async_get_access_token(self) -> str:
        """Request a new access token."""
        try:
            return await self.async_get_access_token()
        except ClientError as err:
            raise AuthException(f"Access token failure: {err}") from err

    @staticmethod
    async def _raise_for_status(resp: ClientResponse) -> ClientResponse:
        """Raise exceptions on failure methods."""
        detail = await AbstractAuth._error_detail(resp)
        try:
            resp.raise_for_status()
        except ClientResponseError as err:
            if err.status == HTTPStatus.FORBIDDEN:
                raise ApiForbiddenException(
                    f"Forbidden response from API: {err}"
                ) from err
            if err.status == HTTPStatus.UNAUTHORIZED:
                raise ApiUnauthorizedException(
                    f"Unable to authenticate with API: {err}"
                ) from err
            detail.append(err.message)
            raise ApiException(": ".join(detail)) from err
        except ClientError as err:
            raise ApiException(f"Error from API: {err}") from err
        return resp

    @staticmethod
    async def _error_detail(resp: ClientResponse) -> list[str]:
        """Return an error message string from the API response."""
        if resp.status < 400:
            return []
        try:
            result = await resp.json()
            error = result.get(ERROR, {})
        except ClientError:
            return []
        message = ["Error from API", f"{resp.status}"]
        if STATUS in error:
            message.append(f"{error[STATUS]}")
        if MESSAGE in error:
            message.append(error[MESSAGE])
        return message
