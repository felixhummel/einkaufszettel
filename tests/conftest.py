from typing import Callable
from ninja.testing.client import NinjaResponse
import pytest

from einkaufszettel.models import Item, Zettel

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


@pytest.fixture
def zettel_netto():
    return Zettel.objects.create(name='Netto')


@pytest.fixture
def zettel_edeka():
    return Zettel.objects.create(name='Edeka')


@pytest.fixture
def netto_items(zettel_netto):
    items = [
        Item.objects.create(
            zettel=zettel_netto,
            name='Apfel',
            qty=1.0,
            unit='Stück',
            completed=False,
        ),
        Item.objects.create(
            zettel=zettel_netto,
            name='Käse',
            qty=1.0,
            unit='Stück',
            completed=True,
        ),
        Item.objects.create(
            zettel=zettel_netto,
            name='Tomaten',
            qty=1.5,
            unit='kg',
            completed=False,
        ),
    ]
    return items
