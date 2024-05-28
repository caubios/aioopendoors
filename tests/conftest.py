"""Test helpers for Opendoors."""

from collections.abc import Generator
from unittest.mock import AsyncMock, patch

import pytest


@pytest.fixture()
def mock_opendoors_client() -> Generator[AsyncMock, None, None]:
    """Mock a Auth Opendoors client."""
    with patch(
        "aioopendoors.auth.AbstractAuth",
        autospec=True,
    ) as mock_client:
        client = mock_client.return_value
        client.get_json.side_effect = get_json_side_effect
        yield client


def get_json_side_effect(arg: str):
    """Return specific json base on parameter."""
    return ""
