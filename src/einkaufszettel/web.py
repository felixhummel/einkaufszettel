from ninja import NinjaAPI, Schema
from ninja.pagination import paginate
from django.shortcuts import get_object_or_404

from typing import List, Optional
from .models import Zettel, Item
from .domain import DEFAULT_UNIT


api = NinjaAPI(title="Einkaufszettel API", version="1.0.0")


# Schemas
class ItemCreateSchema(Schema):
    name: str
    qty: float = 1.0
    unit: str = DEFAULT_UNIT
    completed: bool = False


class ItemUpdateSchema(Schema):
    name: Optional[str] = None
    qty: Optional[float] = None
    unit: Optional[str] = None
    completed: Optional[bool] = None


class ItemSchema(Schema):
    id: int
    name: str
    qty: float
    unit: str
    completed: bool
    created_at: str
    updated_at: str

    @staticmethod
    def resolve_created_at(obj):
        return obj.created_at.isoformat()

    @staticmethod
    def resolve_updated_at(obj):
        return obj.updated_at.isoformat()


class ZettelCreateSchema(Schema):
    name: str


class ZettelUpdateSchema(Schema):
    name: Optional[str] = None


class ZettelSchema(Schema):
    id: int
    name: str
    created_at: str
    updated_at: str
    items: List[ItemSchema] = []

    @staticmethod
    def resolve_created_at(obj):
        return obj.created_at.isoformat()

    @staticmethod
    def resolve_updated_at(obj):
        return obj.updated_at.isoformat()


class ZettelListSchema(Schema):
    id: int
    name: str
    created_at: str
    updated_at: str
    item_count: int

    @staticmethod
    def resolve_created_at(obj):
        return obj.created_at.isoformat()

    @staticmethod
    def resolve_updated_at(obj):
        return obj.updated_at.isoformat()

    @staticmethod
    def resolve_item_count(obj):
        return obj.items.count()


# Zettel endpoints
@api.get("/zettel/", response=List[ZettelListSchema])
@paginate
def list_zettel(request):
    """List all shopping lists"""
    return Zettel.objects.all()


@api.post("/zettel/", response=ZettelSchema)
def create_zettel(request, data: ZettelCreateSchema):
    """Create a new shopping list"""
    zettel = Zettel.objects.create(**data.dict())
    return zettel


@api.get("/zettel/{zettel_id}/", response=ZettelSchema)
def get_zettel(request, zettel_id: int):
    """Get a specific shopping list with all items"""
    zettel = get_object_or_404(Zettel, id=zettel_id)
    return zettel


@api.put("/zettel/{zettel_id}/", response=ZettelSchema)
def update_zettel(request, zettel_id: int, data: ZettelUpdateSchema):
    """Update a shopping list"""
    zettel = get_object_or_404(Zettel, id=zettel_id)
    for attr, value in data.dict(exclude_unset=True).items():
        setattr(zettel, attr, value)
    zettel.save()
    return zettel


@api.delete("/zettel/{zettel_id}/")
def delete_zettel(request, zettel_id: int):
    """Delete a shopping list"""
    zettel = get_object_or_404(Zettel, id=zettel_id)
    zettel.delete()
    return {"success": True}


@api.get("/zettel/{zettel_id}/markdown/")
def get_zettel_markdown(request, zettel_id: int, completed: bool = False):
    """Get shopping list as markdown"""
    zettel = get_object_or_404(Zettel, id=zettel_id)

    # Create domain object for markdown generation
    from .domain import Zettel as DomainZettel, Item as DomainItem

    domain_zettel = DomainZettel(name=zettel.name)
    items = zettel.items.all() if completed else zettel.items.filter(completed=False)

    for item in items:
        domain_item = DomainItem(
            name=item.name,
            qty=item.qty,
            unit=item.unit,
            completed=item.completed
        )
        domain_zettel.append(domain_item)

    return {"markdown": domain_zettel.markdown(completed=completed)}


# Item endpoints
@api.get("/zettel/{zettel_id}/items/", response=List[ItemSchema])
def list_items(request, zettel_id: int, completed: Optional[bool] = None):
    """List items in a shopping list"""
    zettel = get_object_or_404(Zettel, id=zettel_id)
    items = zettel.items.all()

    if completed is not None:
        items = items.filter(completed=completed)

    return items


@api.post("/zettel/{zettel_id}/items/", response=ItemSchema)
def create_item(request, zettel_id: int, data: ItemCreateSchema):
    """Add an item to a shopping list"""
    zettel = get_object_or_404(Zettel, id=zettel_id)
    item = Item.objects.create(zettel=zettel, **data.dict())
    return item


@api.get("/items/{item_id}/", response=ItemSchema)
def get_item(request, item_id: int):
    """Get a specific item"""
    item = get_object_or_404(Item, id=item_id)
    return item


@api.put("/items/{item_id}/", response=ItemSchema)
def update_item(request, item_id: int, data: ItemUpdateSchema):
    """Update an item"""
    item = get_object_or_404(Item, id=item_id)
    for attr, value in data.dict(exclude_unset=True).items():
        setattr(item, attr, value)
    item.save()
    return item


@api.delete("/items/{item_id}/")
def delete_item(request, item_id: int):
    """Delete an item"""
    item = get_object_or_404(Item, id=item_id)
    item.delete()
    return {"success": True}


@api.patch("/items/{item_id}/toggle/", response=ItemSchema)
def toggle_item_completed(request, item_id: int):
    """Toggle the completed status of an item"""
    item = get_object_or_404(Item, id=item_id)
    item.completed = not item.completed
    item.save()
    return item


# Bulk operations
@api.post("/zettel/{zettel_id}/items/bulk/", response=List[ItemSchema])
def bulk_create_items(request, zettel_id: int, items: List[ItemCreateSchema]):
    """Add multiple items to a shopping list"""
    zettel = get_object_or_404(Zettel, id=zettel_id)
    created_items = []

    for item_data in items:
        item = Item.objects.create(zettel=zettel, **item_data.dict())
        created_items.append(item)

    return created_items


@api.patch("/zettel/{zettel_id}/items/complete-all/")
def complete_all_items(request, zettel_id: int):
    """Mark all items in a shopping list as completed"""
    zettel = get_object_or_404(Zettel, id=zettel_id)
    updated_count = zettel.items.filter(completed=False).update(completed=True)
    return {"updated_count": updated_count}


@api.patch("/zettel/{zettel_id}/items/uncomplete-all/")
def uncomplete_all_items(request, zettel_id: int):
    """Mark all items in a shopping list as not completed"""
    zettel = get_object_or_404(Zettel, id=zettel_id)
    updated_count = zettel.items.filter(completed=True).update(completed=False)
    return {"updated_count": updated_count}
