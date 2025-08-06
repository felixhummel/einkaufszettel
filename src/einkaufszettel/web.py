from django.urls import reverse
from ninja import NinjaAPI, Schema
from ninja.security import HttpBearer
from ninja.pagination import paginate
from django.shortcuts import get_object_or_404, render

from typing import List, Optional
from .models import Zettel, Item
from .domain import DEFAULT_UNIT


class GlobalAuth(HttpBearer):
    def authenticate(self, request, token):
        if token == 'geheim':
            return token


api = NinjaAPI(
    auth=GlobalAuth(),
    title='Einkaufszettel API',
    version='1.0.0',
    urls_namespace='ek',
)


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
    slug: str
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
    slug: str
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
    slug: str
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


class Link(Schema):
    url: str
    name: str

    @classmethod
    def from_view_name(cls, name: str):
        url = reverse(name)
        return cls(url=url, name=url)


@api.get('/')
def index(request):
    #  admin/
    # openapi.json [name='openapi-json']
    # docs [name='openapi-view']
    # zettel/ [name='list_zettel']
    links = [
        Link.from_view_name(x)
        for x in [
            'admin:index',
            'ek:openapi-json',
            'ek:openapi-view',
            'ek:list_zettel',
        ]
    ]
    return render(request, 'einkaufszettel/links.txt', {'links': links})


# Zettel endpoints
@api.get('/zettel/', response=List[ZettelListSchema])
@paginate
def list_zettel(request):
    """List all shopping lists"""
    return Zettel.objects.all()


@api.post('/zettel/', response=ZettelSchema)
def create_zettel(request, data: ZettelCreateSchema):
    """Create a new shopping list"""
    zettel = Zettel.objects.create(**data.dict())
    return zettel


@api.get('/zettel/{zettel_slug}/', response=ZettelSchema)
def get_zettel(request, zettel_slug: str):
    """Get a specific shopping list with all items"""
    zettel = get_object_or_404(Zettel, slug=zettel_slug)
    return zettel


@api.put('/zettel/{zettel_slug}/', response=ZettelSchema)
def update_zettel(request, zettel_slug: str, data: ZettelUpdateSchema):
    """Update a shopping list"""
    zettel = get_object_or_404(Zettel, slug=zettel_slug)
    for attr, value in data.dict(exclude_unset=True).items():
        setattr(zettel, attr, value)
    zettel.save()
    return zettel


@api.delete('/zettel/{zettel_slug}/')
def delete_zettel(request, zettel_slug: str):
    """Delete a shopping list"""
    zettel = get_object_or_404(Zettel, slug=zettel_slug)
    zettel.delete()
    return {'success': True}


@api.get('/zettel/{zettel_slug}/markdown/')
def get_zettel_markdown(request, zettel_slug: str, completed: bool = False):
    """Get shopping list as markdown"""
    zettel = get_object_or_404(Zettel, slug=zettel_slug)

    # Create domain object for markdown generation
    from .domain import Zettel as DomainZettel, Item as DomainItem

    domain_zettel = DomainZettel(name=zettel.name)
    items = (
        zettel.items.all()
        if completed
        else zettel.items.filter(completed=False)
    )

    for item in items:
        domain_item = DomainItem(
            name=item.name,
            qty=item.qty,
            unit=item.unit,
            completed=item.completed,
        )
        domain_zettel.append(domain_item)

    return {'markdown': domain_zettel.markdown(completed=completed)}


# Item endpoints
@api.get('/zettel/{zettel_slug}/items/', response=List[ItemSchema])
def list_items(request, zettel_slug: str, completed: Optional[bool] = None):
    """List items in a shopping list"""
    zettel = get_object_or_404(Zettel, slug=zettel_slug)
    items = zettel.items.all()

    if completed is not None:
        items = items.filter(completed=completed)

    return items


@api.post('/zettel/{zettel_slug}/items/', response=ItemSchema)
def create_item(request, zettel_slug: str, data: ItemCreateSchema):
    """Add an item to a shopping list"""
    zettel = get_object_or_404(Zettel, slug=zettel_slug)
    item = Item.objects.create(zettel=zettel, **data.dict())
    return item


@api.get('/zettel/{zettel_slug}/{item_slug}/', response=ItemSchema)
def get_item(request, zettel_slug: str, item_slug: str):
    """Get a specific item"""
    zettel = get_object_or_404(Zettel, slug=zettel_slug)
    item = get_object_or_404(Item, zettel=zettel, slug=item_slug)
    return item


@api.put('/zettel/{zettel_slug}/{item_slug}/', response=ItemSchema)
def update_item(
    request, zettel_slug: str, item_slug: str, data: ItemUpdateSchema
):
    """Update an item"""
    zettel = get_object_or_404(Zettel, slug=zettel_slug)
    item = get_object_or_404(Item, zettel=zettel, slug=item_slug)
    for attr, value in data.dict(exclude_unset=True).items():
        setattr(item, attr, value)
    item.save()
    return item


@api.delete('/zettel/{zettel_slug}/{item_slug}/')
def delete_item(request, zettel_slug: str, item_slug: str):
    """Delete an item"""
    zettel = get_object_or_404(Zettel, slug=zettel_slug)
    item = get_object_or_404(Item, zettel=zettel, slug=item_slug)
    item.delete()
    return {'success': True}


@api.patch('/zettel/{zettel_slug}/{item_slug}/toggle/', response=ItemSchema)
def toggle_item_completed(request, zettel_slug: str, item_slug: str):
    """Toggle the completed status of an item"""
    zettel = get_object_or_404(Zettel, slug=zettel_slug)
    item = get_object_or_404(Item, zettel=zettel, slug=item_slug)
    item.completed = not item.completed
    item.save()
    return item


# Bulk operations
@api.post('/zettel/{zettel_slug}/items/bulk/', response=List[ItemSchema])
def bulk_create_items(
    request, zettel_slug: str, items: List[ItemCreateSchema]
):
    """Add multiple items to a shopping list"""
    zettel = get_object_or_404(Zettel, slug=zettel_slug)
    created_items = []

    for item_data in items:
        item = Item.objects.create(zettel=zettel, **item_data.dict())
        created_items.append(item)

    return created_items


@api.patch('/zettel/{zettel_slug}/items/complete-all/')
def complete_all_items(request, zettel_slug: str):
    """Mark all items in a shopping list as completed"""
    zettel = get_object_or_404(Zettel, slug=zettel_slug)
    updated_count = zettel.items.filter(completed=False).update(completed=True)
    return {'updated_count': updated_count}


@api.patch('/zettel/{zettel_slug}/items/uncomplete-all/')
def uncomplete_all_items(request, zettel_slug: str):
    """Mark all items in a shopping list as not completed"""
    zettel = get_object_or_404(Zettel, slug=zettel_slug)
    updated_count = zettel.items.filter(completed=True).update(completed=False)
    return {'updated_count': updated_count}
