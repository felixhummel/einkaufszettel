# Einkaufszettel Active Context

## Current Work Focus
The project is currently focused on providing a complete REST API for shopping list management with the following capabilities:

- CRUD operations for shopping lists (Zettels)
- CRUD operations for shopping list items
- Markdown export functionality
- Completion status management

## Recent Changes
Based on the migration files, recent database schema evolution includes:

- Initial model creation with basic Zettel and Item structures
- Addition of slug fields to both Zettel and Item models
- Implementation of slug population and uniqueness constraints
- Migration to make slug fields non-nullable

## Next Steps
Potential areas for future development:

- Additional API endpoints for advanced filtering/sorting
- Integration with external shopping services
- Mobile-friendly API responses
- Authentication and user management
- Multi-tenant isolation improvements

## Active Decisions and Considerations
- Using slugify for URL-friendly identifiers while preserving unicode characters
- Keeping API-only approach (no traditional web templates beyond minimal links)
- Supporting both completed and incomplete item views

## Important Patterns and Preferences
- Django Ninja for API development
- Single quotes preferred (ruff configuration)
- Comprehensive type hinting
- 100% test coverage requirement
- Clear migration path for schema changes

## Learnings and Project Insights
- The project demonstrates how to bridge pure Python domain models with Django ORM
- Slug-based routing provides clean, readable URLs
- Markdown export is a simple yet effective way to share shopping lists
- Bulk operations improve API efficiency for multiple item management
