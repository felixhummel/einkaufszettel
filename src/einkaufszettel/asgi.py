import os
import django
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'einkaufszettel.settings')

django.setup()

app = get_asgi_application()
