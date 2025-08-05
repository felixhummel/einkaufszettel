# Einkaufszettel System Patterns

## Architecture Overview
The system follows a domain-driven design pattern with clear separation between business logic and persistence layers:

- **Domain Layer**: Pure Python dataclasses in `domain.py` handle business logic
- **Persistence Layer**: Django ORM models in `models.py` handle data storage
- **API Layer**: Django Ninja endpoints in `web.py` expose functionality via REST API
- **Configuration**: Django settings and URL configuration files

## Key Design Patterns

### Domain-Driven Design
- Domain models (`Item`, `Zettel`) are pure Python dataclasses
- Django models serve as persistence adapters
- Business logic is encapsulated in domain objects
- API layer converts between domain and persistence models

### RESTful API Design
- Resource-based endpoints for zettels and items
- Standard HTTP methods (GET, POST, PUT, DELETE, PATCH)
- Pagination support for list endpoints
- Consistent response schemas using Ninja Schema classes

### Model Relationships
- `Zettel` model represents shopping lists
- `Item` model has foreign key relationship to `Zettel`
- Unique constraint ensures item slugs are unique per zettel
- Slug-based URLs for human-readable resource identification

### Markdown Generation
- Domain models contain markdown generation logic
- API endpoints can export lists as markdown format
- Separation of completed/incomplete items in display

## Component Relationships
```
domain.py (Item, Zettel) ←→ web.py (API endpoints) ←→ models.py (Django ORM)
        ↑                      ↑                            ↑
    Business Logic        API Interface              Persistence Layer
```

## Critical Implementation Paths
1. Domain model to Django model conversion in API endpoints
2. Slug generation and uniqueness constraints
3. Markdown export functionality
4. Bulk operation endpoints
5. Pagination implementation
