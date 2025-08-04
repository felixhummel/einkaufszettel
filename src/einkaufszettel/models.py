from django.db import models
from .domain import DEFAULT_UNIT


class Zettel(models.Model):
    """Shopping list model"""
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

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
    qty = models.FloatField(default=1.0)
    unit = models.CharField(max_length=50, default=DEFAULT_UNIT)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.name} ({self.qty} {self.unit})"
