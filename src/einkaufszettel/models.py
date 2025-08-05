from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify
from .domain import DEFAULT_UNIT


class Zettel(models.Model):
    """Shopping list model"""

    name = models.CharField(max_length=200)
    slug = models.CharField(max_length=200, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['slug']

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class User(AbstractUser):
    """Extended User model"""

    # Add custom fields here if needed
    # Example:
    # phone = models.CharField(max_length=20, blank=True)
    # birth_date = models.DateField(null=True, blank=True)
    pass


class Item(models.Model):
    """Shopping list item model"""

    zettel = models.ForeignKey(
        Zettel, related_name='items', on_delete=models.CASCADE
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, editable=False)
    qty = models.FloatField(default=1.0)
    unit = models.CharField(max_length=50, default=DEFAULT_UNIT)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['slug']
        constraints = [
            models.UniqueConstraint(
                fields=['zettel', 'slug'], name='unique_item_per_zettel'
            )
        ]

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name} ({self.qty} {self.unit})'
