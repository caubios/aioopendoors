"""An example file to use this library."""

import asyncio
import datetime
import logging
import time
from typing import cast

import yaml
from aiohttp import ClientSession, TCPConnector

from aioopendoors.auth import AbstractAuth
from aioopendoors.exceptions import ApiException
from aioopendoors.model import LockActionType, LockAttributes, LockState
from aioopendoors.session import OpendoorSession

_LOGGER = logging.getLogger(__name__)

TIME_TO_PRINT = 1

# Fill out the secrets in secrets.yaml, you can find an example
# _secrets.yaml file, which has to be renamed after filling out the secrets.

with open("src/aioopendoors/secrets.yaml", encoding="UTF-8") as file:
    secrets = yaml.safe_load(file)

CLIENT_ID = secrets["CLIENT_ID"]
CLIENT_SECRET = secrets["CLIENT_SECRET"]
USERNAME = secrets["USERNAME"]
PASSWORD = secrets["PASSWORD"]
AUTH_API_TOKEN_URL = secrets["AUTH_API_TOKEN_URL"]
API_BASE_URL = secrets["API_BASE_URL"]

CLOCK_OUT_OF_SYNC_MAX_SEC = 20


class AsyncTokenAuth(AbstractAuth):
    """Provide Opendoors authentication tied to an OAuth2 based config entry."""

    def __init__(
        self,
        websession: ClientSession,
    ) -> None:
        """Initialize Opendoors auth."""
        super().__init__(websession, API_BASE_URL)
        self.token: dict = {}

    async def async_get_access_token(self) -> str:
        """Return a valid access token."""
        if not self.valid_token:
            await self.async_ensure_token_valid()
        return self.token["access_token"]

    @property
    def valid_token(self) -> bool:
        """Return if token is still valid."""
        if not self.token:
            return False

        return (
            cast(float, self.token["expires_at"])
            > time.time() + CLOCK_OUT_OF_SYNC_MAX_SEC
        )

    async def async_ensure_token_valid(self) -> None:
        """Ensure that the current token is valid."""
        if self.valid_token:
            return

        payload = {
            "grant_type": "password",
            "username": USERNAME,
            "password": PASSWORD,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        }
        async with self.websession.post(AUTH_API_TOKEN_URL, json=payload) as resp:
            result = await resp.json()

        if resp.status == 200:
            result = await resp.json(encoding="UTF-8")
            result["expires_at"] = result["expires_in"] + time.time()
            _LOGGER.info(
                "New token %s will expire at %s",
                result["access_token"],
                datetime.datetime.fromtimestamp(result["expires_at"]),
            )
        if resp.status >= 400:
            raise ApiException(
                f"""The token is invalid, response from
                    Opendoors API: {result}"""
            )
        result["status"] = resp.status
        self.token = cast(dict[str, str], result)


async def main() -> None:
    """Establish connection to lock and print states for TIME_TO_PRINT minutes."""
    websession = ClientSession(connector=TCPConnector(ssl=False))

    api = OpendoorSession(AsyncTokenAuth(websession), poll=True)

    await api.connect()

    # Add a callback to print lock state.
    api.register_locks_callback(callback)

    await asyncio.sleep(5)

    # Change the state of each known lock
    for lock_attribute in api.locks.values():
        action = LockActionType.ACTION_LOCK_LOCK
        if LockState.LOCKED in lock_attribute.state:
            action = LockActionType.ACTION_LOCK_UNLOCK
        _LOGGER.debug("Request for %s", repr(action))
        await api.lock_action(lock_attribute.uid, action)

    # Let the process keep going for a while
    await asyncio.sleep(TIME_TO_PRINT * 60)
    # The close() will stop the websocket and the token refresh tasks
    await api.close()
    await websession.close()


def callback(data: dict[str, LockAttributes]):
    """Process callbacks and print lock info."""
    for lock_attribute in data.values():
        _LOGGER.debug("Lock state is %s", repr(lock_attribute.state))


asyncio.run(main())
