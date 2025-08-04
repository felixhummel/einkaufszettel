#!/usr/bin/env python
"""
Example usage script for the Einkaufszettel Django Ninja API

This script demonstrates how to use the API programmatically with the Django ORM.
For HTTP API usage, see the API_README.md file.
"""

import os
import sys
import django
from django.conf import settings

# Setup Django environment
def setup_django():
    """Configure Django settings for the example"""
    if not settings.configured:
        # Add the src directory to Python path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        src_dir = os.path.join(current_dir, 'src')
        if src_dir not in sys.path:
            sys.path.insert(0, src_dir)

        settings.configure(
            DEBUG=True,
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': ':memory:',  # Use in-memory database for example
                }
            },
            INSTALLED_APPS=[
                'django.contrib.contenttypes',
                'django.contrib.auth',
                'einkaufszettel',
            ],
            SECRET_KEY='example-secret-key',
            USE_TZ=True,
        )
        django.setup()

setup_django()

from einkaufszettel.models import Zettel, Item  # noqa: E402
from einkaufszettel.domain import format_qty  # noqa: E402
from django.db import connection  # noqa: E402


def create_tables():
    """Create database tables for the example"""
    with connection.schema_editor() as schema_editor:
        schema_editor.create_model(Zettel)
        schema_editor.create_model(Item)


def print_separator(title):
    """Print a nice separator for better output formatting"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print('='*60)


def print_zettel(zettel):
    """Print a formatted zettel with all its items"""
    print(f"\n📋 {zettel.name} (ID: {zettel.id})")
    print(f"   Created: {zettel.created_at.strftime('%Y-%m-%d %H:%M:%S')}")

    items = zettel.items.all()
    if not items:
        print("   No items yet")
        return

    print("   Items:")
    for item in items:
        status = "✅" if item.completed else "⬜"
        qty_str = format_qty(item.qty) if item.qty != 1 else ""
        unit_str = item.unit if item.unit != "Stück" else ""
        item_desc = f"{qty_str} {unit_str} {item.name}".strip()
        print(f"   {status} {item_desc}")


def example_basic_operations():
    """Demonstrate basic CRUD operations"""
    print_separator("Basic CRUD Operations")

    # Create shopping lists
    print("\n1. Creating shopping lists...")
    netto_list = Zettel.objects.create(name="Netto Einkauf")
    rewe_list = Zettel.objects.create(name="REWE Großeinkauf")

    print(f"Created: {netto_list.name}")
    print(f"Created: {rewe_list.name}")

    # Add items to the first list
    print("\n2. Adding items to Netto list...")
    items_data = [
        {"name": "Äpfel", "qty": 6, "unit": "Stück"},
        {"name": "Milch", "qty": 1, "unit": "Liter"},
        {"name": "Tomaten", "qty": 1.5, "unit": "kg"},
        {"name": "Brot", "qty": 1, "unit": "Stück"},
    ]

    for item_data in items_data:
        item = Item.objects.create(zettel=netto_list, **item_data)
        print(f"Added: {item.name}")

    # Display the list
    print_zettel(netto_list)

    # Update an item
    print("\n3. Marking Äpfel as completed...")
    apfel_item = netto_list.items.filter(name="Äpfel").first()
    apfel_item.completed = True
    apfel_item.save()

    print_zettel(netto_list)

    # Add items to second list
    print("\n4. Adding items to REWE list...")
    rewe_items = [
        {"name": "Käse", "qty": 200, "unit": "g"},
        {"name": "Joghurt", "qty": 4, "unit": "Stück"},
        {"name": "Nudeln", "qty": 500, "unit": "g"},
    ]

    for item_data in rewe_items:
        Item.objects.create(zettel=rewe_list, **item_data)

    print_zettel(rewe_list)

    return netto_list, rewe_list


def example_bulk_operations(zettel):
    """Demonstrate bulk operations"""
    print_separator("Bulk Operations")

    print(f"\n1. Current state of {zettel.name}:")
    print_zettel(zettel)

    # Complete all items
    print(f"\n2. Completing all items in {zettel.name}...")
    updated_count = zettel.items.filter(completed=False).update(completed=True)
    print(f"Updated {updated_count} items")

    print_zettel(zettel)

    # Add more items
    print(f"\n3. Adding more items to {zettel.name}...")
    new_items = [
        {"name": "Eier", "qty": 12, "unit": "Stück"},
        {"name": "Butter", "qty": 250, "unit": "g"},
        {"name": "Zwiebeln", "qty": 1, "unit": "kg"},
    ]

    for item_data in new_items:
        Item.objects.create(zettel=zettel, **item_data)

    print_zettel(zettel)

    # Uncomplete all items
    print(f"\n4. Resetting all items in {zettel.name}...")
    reset_count = zettel.items.update(completed=False)
    print(f"Reset {reset_count} items")

    print_zettel(zettel)


def example_markdown_generation(zettel):
    """Demonstrate markdown generation using domain objects"""
    print_separator("Markdown Generation")

    # Convert Django model to domain object for markdown generation
    from einkaufszettel.domain import Zettel as DomainZettel, Item as DomainItem

    domain_zettel = DomainZettel(name=zettel.name)

    for item in zettel.items.all():
        domain_item = DomainItem(
            name=item.name,
            qty=item.qty,
            unit=item.unit,
            completed=item.completed
        )
        domain_zettel.append(domain_item)

    print(f"\n1. Markdown for {zettel.name} (incomplete items only):")
    print("```markdown")
    print(domain_zettel.markdown(completed=False))
    print("```")

    print(f"\n2. Markdown for {zettel.name} (all items):")
    print("```markdown")
    print(domain_zettel.markdown(completed=True))
    print("```")


def example_filtering_and_queries():
    """Demonstrate filtering and advanced queries"""
    print_separator("Filtering and Queries")

    # Get all shopping lists
    all_zettel = Zettel.objects.all()
    print(f"\n1. Total shopping lists: {all_zettel.count()}")
    for zettel in all_zettel:
        item_count = zettel.items.count()
        completed_count = zettel.items.filter(completed=True).count()
        print(f"   {zettel.name}: {completed_count}/{item_count} completed")

    # Find incomplete items across all lists
    print("\n2. All incomplete items:")
    incomplete_items = Item.objects.filter(completed=False).select_related('zettel')
    for item in incomplete_items:
        print(f"   {item.zettel.name}: {item.name}")

    # Find items by unit
    print("\n3. Items measured in kg:")
    kg_items = Item.objects.filter(unit='kg')
    for item in kg_items:
        print(f"   {item.name}: {format_qty(item.qty)} kg")

    # Items with quantity > 1
    print("\n4. Items with quantity > 1:")
    bulk_items = Item.objects.filter(qty__gt=1).order_by('-qty')
    for item in bulk_items:
        print(f"   {item.name}: {format_qty(item.qty)} {item.unit}")


def example_statistics():
    """Generate some statistics"""
    print_separator("Statistics")

    total_lists = Zettel.objects.count()
    total_items = Item.objects.count()
    completed_items = Item.objects.filter(completed=True).count()

    print("\n📊 Summary Statistics:")
    print(f"   Total shopping lists: {total_lists}")
    print(f"   Total items: {total_items}")
    print(f"   Completed items: {completed_items}")
    print(f"   Completion rate: {(completed_items/total_items*100):.1f}%" if total_items > 0 else "   Completion rate: 0%")

    # Most common units
    from django.db.models import Count
    unit_stats = Item.objects.values('unit').annotate(count=Count('unit')).order_by('-count')
    print("\n   Most common units:")
    for stat in unit_stats:
        print(f"     {stat['unit']}: {stat['count']} items")


def example_cleanup():
    """Clean up example data"""
    print_separator("Cleanup")

    print("\n1. Deleting all items...")
    deleted_items = Item.objects.all().delete()
    print(f"   Deleted {deleted_items[0]} items")

    print("\n2. Deleting all shopping lists...")
    deleted_zettel = Zettel.objects.all().delete()
    print(f"   Deleted {deleted_zettel[0]} shopping lists")

    print("\n✨ Cleanup complete!")


def main():
    """Run all examples"""
    print("🛒 Einkaufszettel API Example Usage")
    print("This script demonstrates the Django ORM interface.")
    print("For HTTP API usage, see API_README.md")

    # Create database tables
    create_tables()

    try:
        # Run examples
        netto_list, rewe_list = example_basic_operations()
        example_bulk_operations(netto_list)
        example_markdown_generation(netto_list)
        example_filtering_and_queries()
        example_statistics()

        print_separator("Final State")
        print("\nFinal shopping lists:")
        for zettel in Zettel.objects.all():
            print_zettel(zettel)

    except Exception as e:
        print(f"\n❌ Error during example execution: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Clean up
        example_cleanup()

    print_separator("Example Complete")
    print("\n🎉 All examples completed successfully!")
    print("\nNext steps:")
    print("  1. Start the Django development server: python manage.py runserver")
    print("  2. Visit http://localhost:8000/api/docs for interactive API docs")
    print("  3. Use the HTTP API endpoints as documented in API_README.md")


if __name__ == '__main__':
    main()
