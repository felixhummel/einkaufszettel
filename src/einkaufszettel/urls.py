"""
URL configuration for einkaufszettel project.
"""

from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from .web import api


def api_root(request):
    """Simple API root endpoint"""
    return JsonResponse({
        "message": "Welcome to Einkaufszettel API",
        "version": "1.0.0",
        "endpoints": {
            "api_docs": "/api/docs",
            "zettel": "/api/zettel/",
            "items": "/api/items/",
        }
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls),
    path('', api_root, name='api_root'),
]
