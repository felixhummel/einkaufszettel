from django.db import models
from django.utils.text import slugify
from .domain import DEFAULT_UNIT


def generate_unique_slug(model_class, name, exclude_id=None, zettel=None):
    """Generate a unique slug from name for the given model"""
    base_slug = slugify(name)
    if not base_slug:
        base_slug = 'item'

    slug = base_slug
    counter = 1

    while True:
        queryset = model_class.objects.filter(slug=slug)

        # For Item model, check uniqueness within the zettel
        if zettel is not None:
            queryset = queryset.filter(zettel=zettel)

        # Exclude current instance when updating
        if exclude_id:
            queryset = queryset.exclude(id=exclude_id)

        if not queryset.exists():
            return slug

        counter += 1
        slug = f"{base_slug}-{counter}"


class Zettel(models.Model):
    """Shopping list model"""
    name = models.CharField(max_length=200)
    slug = models.CharField(max_length=200, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        self.slug = generate_unique_slug(Zettel, self.name, exclude_id=self.id)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Item(models.Model):
    """Shopping list item model"""
    zettel = models.ForeignKey(
        Zettel,
        related_name='items',
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=200)
    slug = models.CharField(max_length=200, editable=False)
    qty = models.FloatField(default=1.0)
    unit = models.CharField(max_length=50, default=DEFAULT_UNIT)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['zettel', 'slug'],
                name='unique_item_slug_per_zettel'
            )
        ]

    def save(self, *args, **kwargs):
        self.slug = generate_unique_slug(Item, self.name, exclude_id=self.id, zettel=self.zettel)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.qty} {self.unit})"
