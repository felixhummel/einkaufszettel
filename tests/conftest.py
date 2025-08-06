from typing import Callable
from ninja.testing.client import NinjaResponse
import pytest

_DATE_KEYS = ['created_at', 'updated_at']


def remove_keys(data, del_keys):
    if isinstance(data, dict):
        return {
            key: remove_keys(value, del_keys)
            for key, value in data.items()
            if key not in del_keys
        }
    elif isinstance(data, list):
        return [remove_keys(item, del_keys) for item in data]
    else:
        return data


@pytest.fixture
def assert_response_snapshot(snapshot) -> Callable[[NinjaResponse], None]:
    def inner(response, expected_status: int = 200):
        assert response.status_code == expected_status
        response_json = response.json()
        clean_response_json = remove_keys(response_json, _DATE_KEYS)
        assert snapshot('json') == clean_response_json

    return inner
