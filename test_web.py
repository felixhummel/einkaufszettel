import os
import django
from django.conf import settings
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse
import json

# Configure Django settings for testing
if not settings.configured:
    settings.configure(
        DEBUG=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'django.contrib.auth',
            'einkaufszettel',
        ],
        SECRET_KEY='test-secret-key',
        USE_TZ=True,
        ROOT_URLCONF='einkaufszettel.urls',
    )
    django.setup()

from einkaufszettel.models import Zettel, Item


class TestEinkaufszettelAPI(TestCase):
    """Test suite for the Einkaufszettel Django Ninja API"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()

        # Create test zettel
        self.zettel = Zettel.objects.create(name="Test Shopping List")
        self.zettel2 = Zettel.objects.create(name="Another List")

        # Create test items
        self.item1 = Item.objects.create(
            zettel=self.zettel,
            name="Apfel",
            qty=1.0,
            unit="Stück",
            completed=False
        )
        self.item2 = Item.objects.create(
            zettel=self.zettel,
            name="Käse",
            qty=1.0,
            unit="Stück",
            completed=True
        )
        self.item3 = Item.objects.create(
            zettel=self.zettel,
            name="Tomaten",
            qty=1.5,
            unit="kg",
            completed=False
        )

    # Zettel Tests
    def test_list_zettel(self):
        """Test listing all zettel"""
        response = self.client.get('/api/zettel/')
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn('items', data)
        self.assertEqual(len(data['items']), 2)

        # Check that zettel names are present
        names = [item['name'] for item in data['items']]
        self.assertIn("Test Shopping List", names)
        self.assertIn("Another List", names)

    def test_create_zettel(self):
        """Test creating a new zettel"""
        payload = {"name": "New Shopping List"}
        response = self.client.post(
            '/api/zettel/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data['name'], "New Shopping List")
        self.assertIn('id', data)

        # Verify it was created in the database
        zettel = Zettel.objects.get(id=data['id'])
        self.assertEqual(zettel.name, "New Shopping List")

    def test_get_zettel(self):
        """Test getting a specific zettel"""
        response = self.client.get(f'/api/zettel/{self.zettel.id}/')
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data['name'], "Test Shopping List")
        self.assertEqual(data['id'], self.zettel.id)
        self.assertIn('items', data)
        self.assertEqual(len(data['items']), 3)

    def test_get_nonexistent_zettel(self):
        """Test getting a zettel that doesn't exist"""
        response = self.client.get('/api/zettel/99999/')
        self.assertEqual(response.status_code, 404)

    def test_update_zettel(self):
        """Test updating a zettel"""
        payload = {"name": "Updated Shopping List"}
        response = self.client.put(
            f'/api/zettel/{self.zettel.id}/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data['name'], "Updated Shopping List")

        # Verify it was updated in the database
        self.zettel.refresh_from_db()
        self.assertEqual(self.zettel.name, "Updated Shopping List")

    def test_delete_zettel(self):
        """Test deleting a zettel"""
        zettel_id = self.zettel2.id
        response = self.client.delete(f'/api/zettel/{zettel_id}/')
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertTrue(data['success'])

        # Verify it was deleted from the database
        self.assertFalse(Zettel.objects.filter(id=zettel_id).exists())

    def test_get_zettel_markdown(self):
        """Test getting zettel as markdown"""
        response = self.client.get(f'/api/zettel/{self.zettel.id}/markdown/')
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn('markdown', data)
        markdown = data['markdown']

        # Check markdown content
        self.assertIn('# Test Shopping List', markdown)
        self.assertIn('- [ ] Apfel', markdown)
        self.assertIn('- [ ] 1.5 kg Tomaten', markdown)
        # Completed items should not be shown by default
        self.assertNotIn('- [x] Käse', markdown)

    def test_get_zettel_markdown_with_completed(self):
        """Test getting zettel as markdown including completed items"""
        response = self.client.get(f'/api/zettel/{self.zettel.id}/markdown/?completed=true')
        self.assertEqual(response.status_code, 200)

        data = response.json()
        markdown = data['markdown']

        # Should include completed items
        self.assertIn('- [x] Käse', markdown)
        self.assertIn('- [ ] Apfel', markdown)

    # Item Tests
    def test_list_items(self):
        """Test listing items in a zettel"""
        response = self.client.get(f'/api/zettel/{self.zettel.id}/items/')
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(len(data), 3)

        names = [item['name'] for item in data]
        self.assertIn("Apfel", names)
        self.assertIn("Käse", names)
        self.assertIn("Tomaten", names)

    def test_list_items_with_completed_filter(self):
        """Test listing items with completed filter"""
        # Get only uncompleted items
        response = self.client.get(f'/api/zettel/{self.zettel.id}/items/?completed=false')
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(len(data), 2)

        for item in data:
            self.assertFalse(item['completed'])

        # Get only completed items
        response = self.client.get(f'/api/zettel/{self.zettel.id}/items/?completed=true')
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], "Käse")
        self.assertTrue(data[0]['completed'])

    def test_create_item(self):
        """Test creating a new item"""
        payload = {
            "name": "Bananen",
            "qty": 6,
            "unit": "Stück",
            "completed": False
        }
        response = self.client.post(
            f'/api/zettel/{self.zettel.id}/items/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data['name'], "Bananen")
        self.assertEqual(data['qty'], 6)
        self.assertEqual(data['unit'], "Stück")
        self.assertFalse(data['completed'])

        # Verify it was created in the database
        item = Item.objects.get(id=data['id'])
        self.assertEqual(item.name, "Bananen")
        self.assertEqual(item.zettel, self.zettel)

    def test_create_item_with_defaults(self):
        """Test creating item with default values"""
        payload = {"name": "Milk"}
        response = self.client.post(
            f'/api/zettel/{self.zettel.id}/items/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data['name'], "Milk")
        self.assertEqual(data['qty'], 1.0)
        self.assertEqual(data['unit'], "Stück")
        self.assertFalse(data['completed'])

    def test_get_item(self):
        """Test getting a specific item"""
        response = self.client.get(f'/api/items/{self.item1.id}/')
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data['name'], "Apfel")
        self.assertEqual(data['id'], self.item1.id)

    def test_update_item(self):
        """Test updating an item"""
        payload = {
            "name": "Green Apples",
            "qty": 3,
            "completed": True
        }
        response = self.client.put(
            f'/api/items/{self.item1.id}/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data['name'], "Green Apples")
        self.assertEqual(data['qty'], 3)
        self.assertTrue(data['completed'])
        self.assertEqual(data['unit'], "Stück")  # Should remain unchanged

        # Verify in database
        self.item1.refresh_from_db()
        self.assertEqual(self.item1.name, "Green Apples")
        self.assertEqual(self.item1.qty, 3)
        self.assertTrue(self.item1.completed)

    def test_delete_item(self):
        """Test deleting an item"""
        item_id = self.item1.id
        response = self.client.delete(f'/api/items/{item_id}/')
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertTrue(data['success'])

        # Verify it was deleted from the database
        self.assertFalse(Item.objects.filter(id=item_id).exists())

    def test_toggle_item_completed(self):
        """Test toggling item completion status"""
        # Initially, item1 is not completed
        self.assertFalse(self.item1.completed)

        # Toggle to completed
        response = self.client.patch(f'/api/items/{self.item1.id}/toggle/')
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertTrue(data['completed'])

        # Verify in database
        self.item1.refresh_from_db()
        self.assertTrue(self.item1.completed)

        # Toggle back to not completed
        response = self.client.patch(f'/api/items/{self.item1.id}/toggle/')
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertFalse(data['completed'])

    # Bulk Operations Tests
    def test_bulk_create_items(self):
        """Test bulk creating items"""
        payload = [
            {"name": "Bread", "qty": 1, "unit": "loaf"},
            {"name": "Milk", "qty": 2, "unit": "liter"},
            {"name": "Eggs", "qty": 12, "unit": "pieces"}
        ]
        response = self.client.post(
            f'/api/zettel/{self.zettel.id}/items/bulk/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(len(data), 3)

        # Verify all items were created
        names = [item['name'] for item in data]
        self.assertIn("Bread", names)
        self.assertIn("Milk", names)
        self.assertIn("Eggs", names)

        # Verify in database
        total_items = Item.objects.filter(zettel=self.zettel).count()
        self.assertEqual(total_items, 6)  # 3 original + 3 new

    def test_complete_all_items(self):
        """Test marking all items as completed"""
        # Initially, we have 2 uncompleted items
        uncompleted_count = Item.objects.filter(zettel=self.zettel, completed=False).count()
        self.assertEqual(uncompleted_count, 2)

        response = self.client.patch(f'/api/zettel/{self.zettel.id}/items/complete-all/')
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data['updated_count'], 2)

        # Verify all items are now completed
        uncompleted_count = Item.objects.filter(zettel=self.zettel, completed=False).count()
        self.assertEqual(uncompleted_count, 0)

    def test_uncomplete_all_items(self):
        """Test marking all items as not completed"""
        # First, complete all items
        Item.objects.filter(zettel=self.zettel).update(completed=True)

        completed_count = Item.objects.filter(zettel=self.zettel, completed=True).count()
        self.assertEqual(completed_count, 3)

        response = self.client.patch(f'/api/zettel/{self.zettel.id}/items/uncomplete-all/')
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data['updated_count'], 3)

        # Verify all items are now uncompleted
        completed_count = Item.objects.filter(zettel=self.zettel, completed=True).count()
        self.assertEqual(completed_count, 0)

    # Error Handling Tests
    def test_create_item_invalid_zettel(self):
        """Test creating item with invalid zettel ID"""
        payload = {"name": "Test Item"}
        response = self.client.post(
            '/api/zettel/99999/items/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)

    def test_update_nonexistent_item(self):
        """Test updating an item that doesn't exist"""
        payload = {"name": "Updated Item"}
        response = self.client.put(
            '/api/items/99999/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_nonexistent_item(self):
        """Test deleting an item that doesn't exist"""
        response = self.client.delete('/api/items/99999/')
        self.assertEqual(response.status_code, 404)

    def test_empty_zettel_markdown(self):
        """Test markdown generation for empty zettel"""
        empty_zettel = Zettel.objects.create(name="Empty List")
        response = self.client.get(f'/api/zettel/{empty_zettel.id}/markdown/')
        self.assertEqual(response.status_code, 200)

        data = response.json()
        markdown = data['markdown']
        self.assertEqual(markdown.strip(), "# Empty List")
