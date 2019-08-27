from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

from src.forum import routing as forum_routing
from src.rooms import routing as room_routing

websocket_urlpatterns = (forum_routing.websocket_urlpatterns
                         + room_routing.websocket_urlpatterns)

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
