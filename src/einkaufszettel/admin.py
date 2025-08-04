from django.contrib import admin
from .models import Zettel, Item


class ItemInline(admin.TabularInline):
    """Inline admin for items within zettel admin"""
    model = Item
    extra = 1
    fields = ('name', 'qty', 'unit', 'completed')
    ordering = ('created_at',)


@admin.register(Zettel)
class ZettelAdmin(admin.ModelAdmin):
    """Admin configuration for Zettel model"""
    list_display = ('name', 'item_count', 'completed_items', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    inlines = [ItemInline]

    def item_count(self, obj):
        """Return total number of items in this zettel"""
        return obj.items.count()
    item_count.short_description = 'Total Items'

    def completed_items(self, obj):
        """Return number of completed items"""
        completed = obj.items.filter(completed=True).count()
        total = obj.items.count()
        return f"{completed}/{total}"
    completed_items.short_description = 'Completed'


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    """Admin configuration for Item model"""
    list_display = ('name', 'zettel', 'qty', 'unit', 'completed', 'created_at')
    list_filter = ('completed', 'unit', 'zettel', 'created_at')
    search_fields = ('name', 'zettel__name')
    list_editable = ('qty', 'unit', 'completed')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('zettel', 'created_at')

    fieldsets = (
        (None, {
            'fields': ('zettel', 'name', 'qty', 'unit', 'completed')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        """Optimize queryset to reduce database queries"""
        return super().get_queryset(request).select_related('zettel')


# Customize admin site header and title
admin.site.site_header = 'Einkaufszettel Administration'
admin.site.site_title = 'Einkaufszettel Admin'
admin.site.index_title = 'Welcome to Einkaufszettel Administration'
