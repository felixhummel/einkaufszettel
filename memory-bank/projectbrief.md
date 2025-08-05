# Einkaufszettel Project Brief

## Project Overview
Einkaufszettel is a Python-based shopping list management system that provides both programmatic access through Python objects and a web API interface. The name translates to "shopping list" in German.

## Core Purpose
- Manage shopping lists (called "Zettel") programmatically using Python
- Provide a RESTful web API for shopping list operations
- Enable markdown export of shopping lists
- Support item quantities, units, and completion status

## Key Features
- Domain-driven design approach separating business logic from persistence
- Django Ninja API endpoints for CRUD operations
- SQLite database backend
- Markdown generation capabilities
- Slug-based URL routing for API access
- Bulk operations support

## Project Structure
The system combines:
- Python domain models (dataclasses) for core business logic
- Django ORM models for persistence
- REST API endpoints for web access
- Migration system for database schema evolution
