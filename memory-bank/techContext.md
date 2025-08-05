# Einkaufszettel Technical Context

## Technologies Used

### Core Framework
- **Django 4.2+**: Web framework for ORM, admin interface, and URL routing
- **Django Ninja 1.4.3+**: REST API framework built on Django
- **Python 3.11+**: Base language requirement

### Development Tools
- **Uvicorn 0.35.0+**: ASGI server for running the Django application
- **pytest**: Testing framework
- **ruff**: Code linting and formatting
- **pyright**: Type checking
- **django-extensions**: Additional Django utilities
- **django-stubs**: Type stubs for Django
- **ipython**: Enhanced Python interactive shell

### Database
- **SQLite**: Default database backend
- **Django ORM**: Object-relational mapping

### Package Management
- **uv**: Modern Python package installer and resolver
- **pyproject.toml**: Project configuration and dependencies

## Development Setup
1. Install dependencies with `uv sync`
2. Set up environment variables (SECRET_KEY, DEBUG)
3. Run migrations to set up database
4. Use `manage.py` for Django commands
5. Development server with `uvicorn` or Django's runserver

## Technical Constraints
- Python 3.11 minimum version requirement
- Single-tenant focus with multi-tenant ready design
- In-memory shopping list management paradigm
- REST API only (no traditional web interface)
- Markdown export as primary sharing format

## Dependencies Overview
- **Runtime**: django, django-ninja, uvicorn
- **Development**: pytest, ruff, pyright, django-extensions, django-stubs, ipython
- **Testing**: pytest-django, pytest-cov, pytest-env

## Tool Usage Patterns
- Ruff formatting with single quotes
- Pyright type checking in basic mode
- 100% test coverage requirement
- Migration-based database schema evolution
