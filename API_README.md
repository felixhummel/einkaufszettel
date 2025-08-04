# Einkaufszettel API Documentation

A Django Ninja REST API for managing shopping lists (Einkaufszettel) with full CRUD operations, markdown export, and bulk operations.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [API Endpoints](#api-endpoints)
- [Data Models](#data-models)
- [Response Schemas](#response-schemas)
- [Error Handling](#error-handling)
- [Examples](#examples)

## Overview

The Einkaufszettel API provides a complete REST interface for managing shopping lists and their items. Built with Django Ninja, it offers:

- **Full CRUD operations** for shopping lists (Zettel) and items
- **Markdown export** for easy sharing and viewing
- **Bulk operations** for efficient item management
- **Filtering and pagination** support
- **Comprehensive test coverage**

## Installation

1. Install dependencies:
```bash
pip install django django-ninja
```

2. Add to your Django `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'einkaufszettel',
]
```

3. Include in your main `urls.py`:
```python
from einkaufszettel.web import api

urlpatterns = [
    path('api/', api.urls),
    # ... other urls
]
```

4. Run migrations:
```bash
python manage.py makemigrations einkaufszettel
python manage.py migrate
```

## Quick Start

### Create a shopping list and add items:

```bash
# Create a new shopping list
curl -X POST http://localhost:8000/api/zettel/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Weekly Groceries"}'

# Add items to the list (assuming zettel slug is "weekly-groceries")
curl -X POST http://localhost:8000/api/zettel/weekly-groceries/items/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Apfel", "qty": 6, "unit": "Stück"}'

# Get markdown representation
curl http://localhost:8000/api/zettel/weekly-groceries/markdown/
```

## API Endpoints

### Shopping Lists (Zettel)

#### List all shopping lists
```http
GET /api/zettel/
```
**Response:** Paginated list of shopping lists with item counts.

#### Create a shopping list
```http
POST /api/zettel/
Content-Type: application/json

{
  "name": "Shopping List Name"
}
```

#### Get a specific shopping list
```http
GET /api/zettel/{zettel_slug}/
```
**Response:** Complete shopping list with all items.

#### Update a shopping list
```http
PUT /api/zettel/{zettel_slug}/
Content-Type: application/json

{
  "name": "Updated Name"
}
```

#### Delete a shopping list
```http
DELETE /api/zettel/{zettel_slug}/
```

#### Get shopping list as Markdown
```http
GET /api/zettel/{zettel_slug}/markdown/
GET /api/zettel/{zettel_slug}/markdown/?completed=true
```
**Parameters:**
- `completed` (optional): Include completed items in markdown output

### Items

#### List items in a shopping list
```http
GET /api/zettel/{zettel_slug}/items/
GET /api/zettel/{zettel_slug}/items/?completed=false
```
**Parameters:**
- `completed` (optional): Filter by completion status

#### Add an item to a shopping list
```http
POST /api/zettel/{zettel_slug}/items/
Content-Type: application/json

{
  "name": "Item Name",
  "qty": 1.0,
  "unit": "Stück",
  "completed": false
}
```

#### Get a specific item
```http
GET /api/items/{item_slug}/
```

#### Update an item
```http
PUT /api/items/{item_slug}/
Content-Type: application/json

{
  "name": "Updated Name",
  "qty": 2.0,
  "unit": "kg",
  "completed": true
}
```

#### Delete an item
```http
DELETE /api/items/{item_slug}/
```

#### Toggle item completion
```http
PATCH /api/items/{item_slug}/toggle/
```

### Bulk Operations

#### Bulk create items
```http
POST /api/zettel/{zettel_slug}/items/bulk/
Content-Type: application/json

[
  {"name": "Milk", "qty": 1, "unit": "Liter"},
  {"name": "Bread", "qty": 1, "unit": "Stück"},
  {"name": "Eggs", "qty": 12, "unit": "pieces"}
]
```

#### Complete all items
```http
PATCH /api/zettel/{zettel_slug}/items/complete-all/
```

#### Uncomplete all items
```http
PATCH /api/zettel/{zettel_slug}/items/uncomplete-all/
```

## Data Models

### Zettel (Shopping List)
- `slug`: String (auto-generated from name, unique)
- `name`: String (max 200 chars)
- `created_at`: DateTime (auto-generated)
- `updated_at`: DateTime (auto-updated)

### Item
- `slug`: String (auto-generated from name, unique per zettel)
- `zettel`: Foreign key to Zettel
- `name`: String (max 200 chars)
- `qty`: Float (default: 1.0)
- `unit`: String (max 50 chars, default: "Stück")
- `completed`: Boolean (default: false)
- `created_at`: DateTime (auto-generated)
- `updated_at`: DateTime (auto-updated)

## Slug Generation

**⚠️ Important:** The API now uses slugs instead of numeric IDs for identifying resources. Slugs are automatically generated from names and provide human-readable URLs.

### How Slugs Are Generated

1. **Convert to lowercase**: "My Shopping List" → "my shopping list"
2. **Replace spaces with hyphens**: "my shopping list" → "my-shopping-list"
3. **Remove special characters**: "List with émojis! 🛒 & symbols" → "list-with-emojis-symbols"
4. **Ensure uniqueness**: If a slug already exists, append a number

### Examples

| Name | Generated Slug |
|------|----------------|
| "My Shopping List" | `my-shopping-list` |
| "Einkauf für heute!" | `einkauf-fur-heute` |
| "List with émojis 🛒 & symbols" | `list-with-emojis-symbols` |
| "My Shopping List" (duplicate) | `my-shopping-list-2` |
| "UPPERCASE list" | `uppercase-list` |

### Uniqueness Rules

- **Zettel slugs**: Must be unique across all shopping lists
- **Item slugs**: Must be unique within each shopping list (same item name can exist in different lists)

### Automatic Updates

Slugs are automatically regenerated when names change:

```python
# Create a zettel
zettel = Zettel.objects.create(name="Original Name")
print(zettel.slug)  # "original-name"

# Update the name
zettel.name = "Updated Name"
zettel.save()
print(zettel.slug)  # "updated-name"
```

### API Usage

Use slugs in all API endpoints:

```bash
# ✅ Correct - using slug
GET /api/zettel/my-shopping-list/
GET /api/items/milk/

# ❌ Deprecated - using numeric ID
GET /api/zettel/1/
GET /api/items/1/
```

## Response Schemas

### ZettelSchema
```json
{
  "slug": "shopping-list",
  "name": "Shopping List",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z",
  "items": [
    {
      "slug": "apfel",
      "name": "Apfel",
      "qty": 6.0,
      "unit": "Stück",
      "completed": false,
      "created_at": "2024-01-01T12:00:00Z",
      "updated_at": "2024-01-01T12:00:00Z"
    }
  ]
}
```

### ZettelListSchema
```json
{
  "slug": "shopping-list",
  "name": "Shopping List",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z",
  "item_count": 5
}
```

### ItemSchema
```json
{
  "slug": "apfel",
  "name": "Apfel",
  "qty": 6.0,
  "unit": "Stück",
  "completed": false,
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

### Markdown Response
```json
{
  "markdown": "# Shopping List\n- [ ] 6 Apfel\n- [x] Milk\n- [ ] 1.5 kg Tomaten\n"
}
```

## Error Handling

The API returns standard HTTP status codes:

- `200 OK`: Successful operation
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation errors
- `500 Internal Server Error`: Server errors

### Error Response Format
```json
{
  "detail": "Error description"
}
```

## Examples

### Complete Workflow Example

```python
import requests
import json

base_url = "http://localhost:8000/api"

# 1. Create a shopping list
zettel_data = {"name": "Weekly Groceries"}
response = requests.post(f"{base_url}/zettel/", json=zettel_data)
zettel = response.json()
zettel_slug = zettel["slug"]  # "weekly-groceries"

# 2. Add items
items = [
    {"name": "Apfel", "qty": 6, "unit": "Stück"},
    {"name": "Milch", "qty": 1, "unit": "Liter"},
    {"name": "Tomaten", "qty": 1.5, "unit": "kg"}
]

for item in items:
    requests.post(f"{base_url}/zettel/{zettel_slug}/items/", json=item)

# 3. Get current state
response = requests.get(f"{base_url}/zettel/{zettel_slug}/")
print(json.dumps(response.json(), indent=2))

# 4. Mark first item as completed
items_response = requests.get(f"{base_url}/zettel/{zettel_slug}/items/")
first_item_slug = items_response.json()[0]["slug"]  # "apfel"
requests.patch(f"{base_url}/items/{first_item_slug}/toggle/")

# 5. Get markdown representation
markdown_response = requests.get(f"{base_url}/zettel/{zettel_slug}/markdown/")
print(markdown_response.json()["markdown"])

# 6. Complete all remaining items
requests.patch(f"{base_url}/zettel/{zettel_slug}/items/complete-all/")

# 7. Get final markdown with completed items
final_markdown = requests.get(f"{base_url}/zettel/{zettel_slug}/markdown/?completed=true")
print(final_markdown.json()["markdown"])
```

### Markdown Output Format

The API generates markdown in the following format:

```markdown
# Shopping List Name
- [ ] 6 Apfel
- [x] Liter Milch
- [ ] 1.5 kg Tomaten
```

**Format Rules:**
- `[ ]` for incomplete items
- `[x]` for completed items
- Quantity is omitted if it equals 1
- Unit is omitted if it equals "Stück" (default)
- Items are listed in creation order

## Testing

Run the comprehensive test suite:

```bash
# Using Django's test runner
python manage.py test test_web

# Using pytest
pytest test_web.py -v
```

The test suite covers:
- All CRUD operations
- Bulk operations
- Markdown generation
- Error handling
- Edge cases

## Interactive API Documentation

When running the development server, access interactive API documentation at:
- Swagger UI: `http://localhost:8000/api/docs`
- OpenAPI JSON: `http://localhost:8000/api/openapi.json`

## Development Notes

### Default Values
- Default unit: "Stück"
- Default quantity: 1.0
- Default completed status: false

### Pagination
List endpoints support pagination with 20 items per page by default.

### Filtering
Items can be filtered by completion status using the `completed` query parameter.

### Ordering
- Zettel: Ordered by creation date (newest first)
- Items: Ordered by creation date (oldest first)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add comprehensive tests
4. Ensure all tests pass
5. Submit a pull request

## License

This project is licensed under the MIT License.