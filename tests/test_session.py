"""Test opendoors session."""

from typing import TYPE_CHECKING

from aioopendoors.auth import AbstractAuth
from aioopendoors.session import OpendoorSession


async def test_connect_disconnect(mock_opendoors_client: AbstractAuth):
    """Test opendoors session commands."""
    opendoors_api = OpendoorSession(mock_opendoors_client, poll=True)
    await opendoors_api.connect()
    await opendoors_api.close()
    if TYPE_CHECKING:
        assert opendoors_api.rest_task is not None
    assert opendoors_api.rest_task.cancelled()
