"""
ASGI config for tutoring project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack

import os

import tutoringapp.routing


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ikechen.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket" : AuthMiddlewareStack(
        URLRouter(
            tutoringapp.routing.websocket_urlpatterns
        )
    )
})