from django.urls import re_path
from . import consumers

# re_path  allow to define routings using regular expression

#  Defines a URL route for WebSocket connections in a Django Channels application. 
#  It matches incoming WebSocket requests directed to a path like ws://example.com/ws/chat/room123/, 
#  where room123 is captured as a named group called room_name.
#  This captured room_name is then available within the consumer's scope dictionary, 
#  allowing the application to handle different chat rooms dynamically.
#  The as_asgi() method converts the ChatConsumer class into an ASGI application, 
#  which will instantiate a new consumer instance for each incoming WebSocket connection
websocket_patterns = [
    #re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
    #re_path(r'ws/chat/(?P<room_name>[^/]+)/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'^ws/chat/(?P<room_name>[^/]+)/$', consumers.ChatConsumer.as_asgi()),
]