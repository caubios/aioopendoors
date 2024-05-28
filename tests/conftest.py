"""Test helpers for Opendoors."""

import json
from collections.abc import Generator
from unittest.mock import AsyncMock, patch

import pytest

from tests import load_fixture


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
    if arg.startswith("index.php?page=account/get_authorization_list"):
        return json.loads(load_fixture("autorisationslist.json"))
    if arg.startswith("index.php?page=actuator/list"):
        return json.loads(load_fixture("actuatorslist.json"))
    if arg.startswith("index.php?page=actuator/get_status"):
        return json.loads(load_fixture("getstatus.json"))
    if arg.startswith("index.php?page=gateway/store_action"):
        return json.loads(load_fixture("storeaction.json"))
    if arg.startswith("index.php?page=gateway/get_action"):
        return json.loads(load_fixture("getaction.json"))
    return ""
