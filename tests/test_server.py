import pytest
from ninja.testing import TestClient

from einkaufszettel.models import Zettel, Item
from einkaufszettel.web import api

# Enable DB for all tests in this module
pytestmark = pytest.mark.django_db


BEARER_TOKEN = 'geheim'
client = TestClient(api, headers={'Authorization': f'Bearer {BEARER_TOKEN}'})


def test_list_zettel(assert_response_snapshot, zettel_netto, zettel_edeka):
    response = client.get('/zettel/')
    assert_response_snapshot(response)


def test_create_zettel(assert_response_snapshot):
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


def test_get_zettel(assert_response_snapshot, zettel_netto, netto_items):
    assert_response_snapshot(client.get(f'/zettel/{zettel_netto.slug}/'))


def test_get_nonexistent_zettel(assert_response_snapshot):
    response = client.get('/zettel/non-existent-slug/')
    assert_response_snapshot(response, expected_status=404)


def test_update_zettel(assert_response_snapshot, zettel_netto):
    payload = {'name': 'Updated Shopping List'}
    response = client.put(
        f'/zettel/{zettel_netto.slug}/',
        json=payload,
    )
    assert_response_snapshot(response)

    # Verify it was updated in the database
    zettel_netto.refresh_from_db()
    assert zettel_netto.name == 'Updated Shopping List'


def test_delete_zettel(assert_response_snapshot, zettel_edeka):
    zettel_slug = zettel_edeka.slug
    response = client.delete(f'/zettel/{zettel_slug}/')
    assert_response_snapshot(response)

    # Verify it was deleted from the database
    assert not Zettel.objects.filter(slug=zettel_slug).exists()


def test_get_zettel_markdown(snapshot, zettel_netto, netto_items):
    response = client.get(f'/zettel/{zettel_netto.slug}/markdown/')
    assert response.status_code == 200

    data = response.json()
    assert snapshot() == data['markdown']


def test_get_zettel_markdown_with_completed(
    assert_response_snapshot, zettel_netto, netto_items
):
    response = client.get(
        f'/zettel/{zettel_netto.slug}/markdown/?completed=true'
    )
    assert_response_snapshot(response)


# Item Tests
def test_list_items(assert_response_snapshot, zettel_netto, netto_items):
    response = client.get(f'/zettel/{zettel_netto.slug}/items/')
    assert_response_snapshot(response)


def test_list_items_with_completed_filter(
    assert_response_snapshot, zettel_netto, netto_items
):
    # Get only uncompleted items
    response = client.get(
        f'/zettel/{zettel_netto.slug}/items/?completed=false'
    )
    assert_response_snapshot(response)

    # Get only completed items
    response = client.get(f'/zettel/{zettel_netto.slug}/items/?completed=true')
    assert_response_snapshot(response)


def test_create_item(assert_response_snapshot, zettel_netto):
    payload = {
        'name': 'Bananen',
        'qty': 6,
        'unit': 'Stück',
        'completed': False,
    }
    response = client.post(
        f'/zettel/{zettel_netto.slug}/items/',
        json=payload,
    )
    assert_response_snapshot(response)

    data = response.json()
    # Verify it was created in the database
    item = Item.objects.get(slug=data['slug'])
    assert item.name == 'Bananen'
    assert item.zettel == zettel_netto


def test_create_item_with_defaults(assert_response_snapshot, zettel_netto):
    payload = {'name': 'Milk'}
    response = client.post(
        f'/zettel/{zettel_netto.slug}/items/',
        json=payload,
    )
    assert_response_snapshot(response)


def test_get_item(assert_response_snapshot, zettel_netto, netto_items):
    item1 = netto_items[0]
    response = client.get(f'/zettel/{zettel_netto.slug}/{item1.slug}/')
    assert_response_snapshot(response)


def test_update_item(assert_response_snapshot, zettel_netto, netto_items):
    item1 = netto_items[0]
    payload = {'name': 'Green Apples', 'qty': 3, 'completed': True}
    response = client.put(
        f'/zettel/{zettel_netto.slug}/{item1.slug}/',
        json=payload,
    )
    assert_response_snapshot(response)

    # Verify in database
    item1.refresh_from_db()
    assert item1.name == 'Green Apples'
    assert item1.qty == 3
    assert item1.completed


def test_delete_item(assert_response_snapshot, zettel_netto, netto_items):
    item1 = netto_items[0]
    item_slug = item1.slug
    response = client.delete(f'/zettel/{zettel_netto.slug}/{item_slug}/')
    assert_response_snapshot(response)

    # Verify it was deleted from the database
    assert not Item.objects.filter(slug=item_slug).exists()


def test_toggle_item_completed(
    assert_response_snapshot, zettel_netto, netto_items
):
    item1 = netto_items[0]
    # Initially, item1 is not completed
    assert not item1.completed

    # Toggle to completed
    response = client.patch(
        f'/zettel/{zettel_netto.slug}/{item1.slug}/toggle/'
    )
    assert_response_snapshot(response)

    data = response.json()
    # Verify in database
    item1.refresh_from_db()
    assert item1.completed

    # Toggle back to not completed
    response = client.patch(
        f'/zettel/{zettel_netto.slug}/{item1.slug}/toggle/'
    )
    assert_response_snapshot(response)

    data = response.json()
    assert not data['completed']


# Bulk Operations Tests
def test_bulk_create_items(assert_response_snapshot, zettel_netto):
    payload = [
        {'name': 'Bread', 'qty': 1, 'unit': 'loaf'},
        {'name': 'Milk', 'qty': 2, 'unit': 'liter'},
        {'name': 'Eggs', 'qty': 12, 'unit': 'pieces'},
    ]
    response = client.post(
        f'/zettel/{zettel_netto.slug}/items/bulk/',
        json=payload,
    )
    assert_response_snapshot(response)

    # Verify in database
    total_items = Item.objects.filter(zettel=zettel_netto).count()
    assert total_items == 3  # 3 new items


def test_complete_all_items(
    assert_response_snapshot, zettel_netto, netto_items
):
    # Initially, we have 2 uncompleted items
    uncompleted_count = Item.objects.filter(
        zettel=zettel_netto, completed=False
    ).count()
    assert uncompleted_count == 2

    response = client.patch(f'/zettel/{zettel_netto.slug}/items/complete-all/')
    assert_response_snapshot(response)

    # Verify all items are now completed
    uncompleted_count = Item.objects.filter(
        zettel=zettel_netto, completed=False
    ).count()
    assert uncompleted_count == 0


def test_uncomplete_all_items(
    assert_response_snapshot, zettel_netto, netto_items
):
    # First, complete all items
    Item.objects.filter(zettel=zettel_netto).update(completed=True)

    completed_count = Item.objects.filter(
        zettel=zettel_netto, completed=True
    ).count()
    assert completed_count == 3

    response = client.patch(
        f'/zettel/{zettel_netto.slug}/items/uncomplete-all/'
    )
    assert_response_snapshot(response)

    # Verify all items are now uncompleted
    completed_count = Item.objects.filter(
        zettel=zettel_netto, completed=True
    ).count()
    assert completed_count == 0


# Error Handling Tests
def test_create_item_invalid_zettel(assert_response_snapshot):
    payload = {'name': 'Test Item'}
    response = client.post(
        '/zettel/non-existent-slug/items/',
        json=payload,
    )
    assert_response_snapshot(response, expected_status=404)


def test_update_nonexistent_item(assert_response_snapshot, zettel_netto):
    payload = {'name': 'Updated Item'}
    response = client.put(
        f'/zettel/{zettel_netto.slug}/non-existent-slug/',
        json=payload,
    )
    assert_response_snapshot(response, expected_status=404)


def test_delete_nonexistent_item(assert_response_snapshot, zettel_netto):
    response = client.delete(f'/zettel/{zettel_netto.slug}/non-existent-slug/')
    assert_response_snapshot(response, expected_status=404)


def test_hierarchical_access_control_get_item(
    assert_response_snapshot, zettel_netto, zettel_edeka, netto_items
):
    item1 = netto_items[0]
    # Try to access item1 (belongs to zettel_netto) through zettel_edeka path
    response = client.get(f'/zettel/{zettel_edeka.slug}/{item1.slug}/')
    assert_response_snapshot(response, expected_status=404)


def test_hierarchical_access_control_update_item(
    assert_response_snapshot, zettel_netto, zettel_edeka, netto_items
):
    item1 = netto_items[0]
    payload = {'name': 'Hacked Item'}
    response = client.put(
        f'/zettel/{zettel_edeka.slug}/{item1.slug}/',
        json=payload,
    )
    assert_response_snapshot(response, expected_status=404)

    # Verify the item wasn't changed
    item1.refresh_from_db()
    assert item1.name == 'Apfel'


def test_hierarchical_access_control_delete_item(
    assert_response_snapshot, zettel_netto, zettel_edeka, netto_items
):
    item1 = netto_items[0]
    response = client.delete(f'/zettel/{zettel_edeka.slug}/{item1.slug}/')
    assert_response_snapshot(response, expected_status=404)

    # Verify the item still exists
    assert Item.objects.filter(slug=item1.slug).exists()


def test_hierarchical_access_control_toggle_item(
    assert_response_snapshot, zettel_netto, zettel_edeka, netto_items
):
    item1 = netto_items[0]
    original_completed = item1.completed
    response = client.patch(
        f'/zettel/{zettel_edeka.slug}/{item1.slug}/toggle/'
    )
    assert_response_snapshot(response, expected_status=404)

    # Verify the item's completed status wasn't changed
    item1.refresh_from_db()
    assert item1.completed == original_completed


def test_empty_zettel_markdown(assert_response_snapshot):
    empty_zettel = Zettel.objects.create(name='Empty List')
    response = client.get(f'/zettel/{empty_zettel.slug}/markdown/')
    assert_response_snapshot(response)
