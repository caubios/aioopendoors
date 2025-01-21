"""Module to connect to Lock."""

import asyncio
import contextlib
import logging

from .auth import AbstractAuth
from .exceptions import NoDataAvailableException
from .model import LockAction, LockActionState, LockAttributes, LockStatus

_LOGGER = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)

REST_POLL_CYCLE = 10
REST_LOCK_ACTION_POLL_CYCLE = 1


class OpendoorSession:
    """Opendoor API to communicate with an Lock.

    The `LockSession` is the primary API service for this library. It supports
    operations like getting a status or sending commands.
    """

    def __init__(
        self,
        auth: AbstractAuth,
        poll: bool = False,
    ) -> None:
        """Create a session.

        :param class auth: The AbstractAuth class from opendoor.auth.
        :param bool poll: Session will poll locks data if True.
        """
        self.auth = auth
        self.locks_update_cbs: list = []
        self.locks: dict[str, LockAttributes] = {}
        self.loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()
        self.poll = poll
        self.rest_task: asyncio.Task | None = None
        self.sites: list[str] = []

    def register_locks_callback(self, callback) -> None:
        """Register a locks update callback."""
        if callback not in self.locks_update_cbs:
            self.locks_update_cbs.append(callback)

    def _schedule_locks_callback(self, cb) -> None:
        """Schedule a locks callback."""
        if self.poll and self.locks is None:
            raise NoDataAvailableException
        self.loop.call_soon_threadsafe(cb, self.locks)

    def _schedule_locks_callbacks(self) -> None:
        """Schedule a locks callbacks."""
        for cb in self.locks_update_cbs:
            self._schedule_locks_callback(cb)

    def unregister_locks_callback(self, callback) -> None:
        """Unregister a locks update callback.

        :param func callback: Takes one function, which should be unregistered.
        """
        if callback in self.locks_update_cbs:
            self.locks_update_cbs.remove(callback)

    async def connect(self) -> None:
        """Connect to the API.

        This method handle the login. Also a REST task will be started, which
        periodically polls the REST endpoint, when polling is set to true.
        """
        if self.poll:
            await self.discover()
            self.rest_task = asyncio.create_task(self._rest_task())

    async def discover(self) -> dict[str, LockAttributes]:
        """Discover all the lock and return a dictionary of Data."""
        _dict = {}

        # First we want to get all siteId from user authorization
        url = "index.php?page=account/get_authorization_list&json=true"
        site_list = await self.auth.get_json(url)
        for site in site_list["AUTHORIZATIONS"]:
            site_id = site["SITE_ID"]
            self.sites.append(site_id)
            # Then we want to gather all LockAttributes for all siteIds
            url = f"index.php?page=actuator/list&json=true&SITE_ID={site_id}"
            lock_list = await self.auth.get_json(url)
            for lock in lock_list["ACTUATOR_LIST"]:
                lock_attribute = LockAttributes.from_dict(lock)
                _dict[lock_attribute.uid] = lock_attribute

        self.locks = _dict
        return _dict

    async def update_status(self) -> dict[str, LockAttributes]:
        """Update status."""

        for site_id in self.sites:
            url = f"index.php?page=actuator/get_status&json=true&SITE_ID={site_id}"
            raw_lock_data = await self.auth.get_json(url)
            for raw_lock_status in raw_lock_data["ACTUATOR_LIST"]:
                lock_status = LockStatus.from_dict(raw_lock_status)
                self.locks[lock_status.uid] = self._update_lock_status(
                    self.locks[lock_status.uid], lock_status
                )
                if self.locks[lock_status.uid].action is not None:
                    await self.update_action(lock_status.uid)
        return self.locks

    async def lock_action(self, lock_id: str, lock_action: int) -> LockAction:
        """Request an action on a lock."""

        url = (
            "index.php?page=gateway/store_action"
            "&json=true"
            f"&dv={lock_id}"
            f"&a={lock_action!s}"
        )
        raw_lock_data = await self.auth.get_json(url)
        action = LockAction.from_dict(raw_lock_data)
        self.locks[lock_id].action = action
        return action

    async def update_action(self, lock_id: str) -> LockAction | None:
        """Update status of last action for a lock."""

        action = self.locks[lock_id].action
        if action is not None:
            if action.action_state != LockActionState.ACTION_STATE_SUCCESS:
                url = f"index.php?page=gateway/get_action&json=true&a={action.id}"
                raw_action_update = await self.auth.get_json(url)
                action_update = LockAction.from_dict(raw_action_update)
                self.locks[lock_id].action = action_update
                return action_update
        self.locks[lock_id].action = None
        return None

    async def _rest_task(self) -> None:
        """Poll data periodically via Rest."""

        while True:
            await self.update_status()
            self._schedule_locks_callbacks()
            await asyncio.sleep(REST_POLL_CYCLE)

    async def close(self) -> None:
        """Close the session."""

        if self.rest_task:
            if not self.rest_task.cancelled():
                self.rest_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await asyncio.gather(self.rest_task)

    @staticmethod
    def _update_lock_status(
        attributes: LockAttributes, status: LockStatus
    ) -> LockAttributes:
        """Update LockAttributes with latest status."""

        if attributes.uid == status.uid:
            attributes.errors = status.errors
            attributes.state = status.state
            attributes.door_state = status.door_state
            attributes.download_update = status.download_update

        return attributes
