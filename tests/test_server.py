from typing import Callable
from ninja.testing.client import NinjaResponse
import pytest
from ninja.testing import TestClient

from einkaufszettel.models import Zettel, Item
from einkaufszettel.web import api

# Enable DB for all tests in this module
pytestmark = pytest.mark.django_db

# Create test client
client = TestClient(api)


@pytest.fixture
def test_zettel():
    return Zettel.objects.create(name='Netto')


@pytest.fixture
def another_zettel():
    return Zettel.objects.create(name='Edeka')


@pytest.fixture
def test_items(test_zettel):
    items = [
        Item.objects.create(
            zettel=test_zettel,
            name='Apfel',
            qty=1.0,
            unit='Stück',
            completed=False,
        ),
        Item.objects.create(
            zettel=test_zettel,
            name='Käse',
            qty=1.0,
            unit='Stück',
            completed=True,
        ),
        Item.objects.create(
            zettel=test_zettel,
            name='Tomaten',
            qty=1.5,
            unit='kg',
            completed=False,
        ),
    ]
    return items


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


def test_list_zettel(assert_response_snapshot, test_zettel, another_zettel):
    """Test listing all zettel"""
    response = client.get('/zettel/')
    assert_response_snapshot(response)


def test_create_zettel(assert_response_snapshot):
    """Test creating a new zettel"""
    payload = {'name': 'New Shopping List'}
    response = client.post(
        '/zettel/',
        json=payload,
    )
    assert_response_snapshot(response)

    data = response.json()
    # Verify it was created in the database
    zettel = Zettel.objects.get(slug=data['slug'])
    assert zettel.name == 'New Shopping List'


def test_get_zettel(assert_response_snapshot, test_zettel, test_items):
    """Test getting a specific zettel"""
    assert_response_snapshot(client.get(f'/zettel/{test_zettel.slug}/'))


def test_get_nonexistent_zettel(assert_response_snapshot):
    """Test getting a zettel that doesn't exist"""
    response = client.get('/zettel/non-existent-slug/')
    assert_response_snapshot(response, expected_status=404)


def test_update_zettel(assert_response_snapshot, test_zettel):
    """Test updating a zettel"""
    payload = {'name': 'Updated Shopping List'}
    response = client.put(
        f'/zettel/{test_zettel.slug}/',
        json=payload,
    )
    assert_response_snapshot(response)

    # Verify it was updated in the database
    test_zettel.refresh_from_db()
    assert test_zettel.name == 'Updated Shopping List'


def test_delete_zettel(assert_response_snapshot, another_zettel):
    """Test deleting a zettel"""
    zettel_slug = another_zettel.slug
    response = client.delete(f'/zettel/{zettel_slug}/')
    assert_response_snapshot(response)

    # Verify it was deleted from the database
    assert not Zettel.objects.filter(slug=zettel_slug).exists()


def test_get_zettel_markdown(snapshot, test_zettel, test_items):
    """Test getting zettel as markdown"""
    response = client.get(f'/zettel/{test_zettel.slug}/markdown/')
    assert response.status_code == 200

    data = response.json()
    assert snapshot() == data['markdown']


def test_get_zettel_markdown_with_completed(
    assert_response_snapshot, test_zettel, test_items
):
    """Test getting zettel as markdown including completed items"""
    response = client.get(
        f'/zettel/{test_zettel.slug}/markdown/?completed=true'
    )
    assert_response_snapshot(response)


# Item Tests
def test_list_items(assert_response_snapshot, test_zettel, test_items):
    """Test listing items in a zettel"""
    response = client.get(f'/zettel/{test_zettel.slug}/items/')
    assert_response_snapshot(response)


def test_list_items_with_completed_filter(
    assert_response_snapshot, test_zettel, test_items
):
    """Test listing items with completed filter"""
    # Get only uncompleted items
    response = client.get(f'/zettel/{test_zettel.slug}/items/?completed=false')
    assert_response_snapshot(response)

    # Get only completed items
    response = client.get(f'/zettel/{test_zettel.slug}/items/?completed=true')
    assert_response_snapshot(response)


def test_create_item(assert_response_snapshot, test_zettel):
    """Test creating a new item"""
    payload = {
        'name': 'Bananen',
        'qty': 6,
        'unit': 'Stück',
        'completed': False,
    }
    response = client.post(
        f'/zettel/{test_zettel.slug}/items/',
        json=payload,
    )
    assert_response_snapshot(response)

    data = response.json()
    # Verify it was created in the database
    item = Item.objects.get(slug=data['slug'])
    assert item.name == 'Bananen'
    assert item.zettel == test_zettel


def test_create_item_with_defaults(assert_response_snapshot, test_zettel):
    """Test creating item with default values"""
    payload = {'name': 'Milk'}
    response = client.post(
        f'/zettel/{test_zettel.slug}/items/',
        json=payload,
    )
    assert_response_snapshot(response)


def test_get_item(assert_response_snapshot, test_zettel, test_items):
    """Test getting a specific item"""
    item1 = test_items[0]
    response = client.get(f'/zettel/{test_zettel.slug}/{item1.slug}/')
    assert_response_snapshot(response)


def test_update_item(assert_response_snapshot, test_zettel, test_items):
    """Test updating an item"""
    item1 = test_items[0]
    payload = {'name': 'Green Apples', 'qty': 3, 'completed': True}
    response = client.put(
        f'/zettel/{test_zettel.slug}/{item1.slug}/',
        json=payload,
    )
    assert_response_snapshot(response)

    # Verify in database
    item1.refresh_from_db()
    assert item1.name == 'Green Apples'
    assert item1.qty == 3
    assert item1.completed


def test_delete_item(assert_response_snapshot, test_zettel, test_items):
    """Test deleting an item"""
    item1 = test_items[0]
    item_slug = item1.slug
    response = client.delete(f'/zettel/{test_zettel.slug}/{item_slug}/')
    assert_response_snapshot(response)

    # Verify it was deleted from the database
    assert not Item.objects.filter(slug=item_slug).exists()


def test_toggle_item_completed(
    assert_response_snapshot, test_zettel, test_items
):
    """Test toggling item completion status"""
    item1 = test_items[0]
    # Initially, item1 is not completed
    assert not item1.completed

    # Toggle to completed
    response = client.patch(f'/zettel/{test_zettel.slug}/{item1.slug}/toggle/')
    assert_response_snapshot(response)

    data = response.json()
    # Verify in database
    item1.refresh_from_db()
    assert item1.completed

    # Toggle back to not completed
    response = client.patch(f'/zettel/{test_zettel.slug}/{item1.slug}/toggle/')
    assert_response_snapshot(response)

    data = response.json()
    assert not data['completed']


# Bulk Operations Tests
def test_bulk_create_items(assert_response_snapshot, test_zettel):
    """Test bulk creating items"""
    payload = [
        {'name': 'Bread', 'qty': 1, 'unit': 'loaf'},
        {'name': 'Milk', 'qty': 2, 'unit': 'liter'},
        {'name': 'Eggs', 'qty': 12, 'unit': 'pieces'},
    ]
    response = client.post(
        f'/zettel/{test_zettel.slug}/items/bulk/',
        json=payload,
    )
    assert_response_snapshot(response)

    # Verify in database
    total_items = Item.objects.filter(zettel=test_zettel).count()
    assert total_items == 3  # 3 new items


def test_complete_all_items(assert_response_snapshot, test_zettel, test_items):
    """Test marking all items as completed"""
    # Initially, we have 2 uncompleted items
    uncompleted_count = Item.objects.filter(
        zettel=test_zettel, completed=False
    ).count()
    assert uncompleted_count == 2

    response = client.patch(f'/zettel/{test_zettel.slug}/items/complete-all/')
    assert_response_snapshot(response)

    # Verify all items are now completed
    uncompleted_count = Item.objects.filter(
        zettel=test_zettel, completed=False
    ).count()
    assert uncompleted_count == 0


def test_uncomplete_all_items(
    assert_response_snapshot, test_zettel, test_items
):
    """Test marking all items as not completed"""
    # First, complete all items
    Item.objects.filter(zettel=test_zettel).update(completed=True)

    completed_count = Item.objects.filter(
        zettel=test_zettel, completed=True
    ).count()
    assert completed_count == 3

    response = client.patch(
        f'/zettel/{test_zettel.slug}/items/uncomplete-all/'
    )
    assert_response_snapshot(response)

    # Verify all items are now uncompleted
    completed_count = Item.objects.filter(
        zettel=test_zettel, completed=True
    ).count()
    assert completed_count == 0


# Error Handling Tests
def test_create_item_invalid_zettel(assert_response_snapshot):
    """Test creating item with invalid zettel ID"""
    payload = {'name': 'Test Item'}
    response = client.post(
        '/zettel/non-existent-slug/items/',
        json=payload,
    )
    assert_response_snapshot(response, expected_status=404)


def test_update_nonexistent_item(assert_response_snapshot, test_zettel):
    """Test updating an item that doesn't exist"""
    payload = {'name': 'Updated Item'}
    response = client.put(
        f'/zettel/{test_zettel.slug}/non-existent-slug/',
        json=payload,
    )
    assert_response_snapshot(response, expected_status=404)


def test_delete_nonexistent_item(assert_response_snapshot, test_zettel):
    """Test deleting an item that doesn't exist"""
    response = client.delete(f'/zettel/{test_zettel.slug}/non-existent-slug/')
    assert_response_snapshot(response, expected_status=404)


def test_hierarchical_access_control_get_item(
    assert_response_snapshot, test_zettel, another_zettel, test_items
):
    """Test that items can't be accessed through wrong zettel path"""
    item1 = test_items[0]
    # Try to access item1 (belongs to test_zettel) through another_zettel path
    response = client.get(f'/zettel/{another_zettel.slug}/{item1.slug}/')
    assert_response_snapshot(response, expected_status=404)


def test_hierarchical_access_control_update_item(
    assert_response_snapshot, test_zettel, another_zettel, test_items
):
    """Test that items can't be updated through wrong zettel path"""
    item1 = test_items[0]
    payload = {'name': 'Hacked Item'}
    response = client.put(
        f'/zettel/{another_zettel.slug}/{item1.slug}/',
        json=payload,
    )
    assert_response_snapshot(response, expected_status=404)

    # Verify the item wasn't changed
    item1.refresh_from_db()
    assert item1.name == 'Apfel'


def test_hierarchical_access_control_delete_item(
    assert_response_snapshot, test_zettel, another_zettel, test_items
):
    """Test that items can't be deleted through wrong zettel path"""
    item1 = test_items[0]
    response = client.delete(f'/zettel/{another_zettel.slug}/{item1.slug}/')
    assert_response_snapshot(response, expected_status=404)

    # Verify the item still exists
    assert Item.objects.filter(slug=item1.slug).exists()


def test_hierarchical_access_control_toggle_item(
    assert_response_snapshot, test_zettel, another_zettel, test_items
):
    """Test that items can't be toggled through wrong zettel path"""
    item1 = test_items[0]
    original_completed = item1.completed
    response = client.patch(
        f'/zettel/{another_zettel.slug}/{item1.slug}/toggle/'
    )
    assert_response_snapshot(response, expected_status=404)

    # Verify the item's completed status wasn't changed
    item1.refresh_from_db()
    assert item1.completed == original_completed


def test_empty_zettel_markdown(assert_response_snapshot):
    """Test markdown generation for empty zettel"""
    empty_zettel = Zettel.objects.create(name='Empty List')
    response = client.get(f'/zettel/{empty_zettel.slug}/markdown/')
    assert_response_snapshot(response)
