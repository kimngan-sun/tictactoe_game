import os
from channels.auth import AuthMiddlewareStack 
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from game.consumers import *
from django.urls import path

os.environ.setdefault('DJANGO_SETTINGS_MODULE','tictactoe.settings')
application = get_asgi_application()
application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter([
            path("ws/game/<str:code>/", GameConsumer.as_asgi()),
        ])
    ),
})