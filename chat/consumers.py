import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import Room, Message

class ChatConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_name = None
        self.room_group_name = None
        self.room = None
        self.user = None
        self.user_inbox = None

    def connect(self):
        # we called accept() in order to accept the connection. 
        # After that, we added the user to the channel layer group
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        self.room = Room.objects.get(name=self.room_name)
        self.user = self.scope['user']
        # create a private inbox for that user to accept private messages
        self.user_inbox = f'inbox_{self.user.username}'

        #connection has be accepted
        self.accept()

        # It adds the current WebSocket consumer instance to a named group so it can receive broadcast messages sent to that group.
        # async_to_sync() - Converts an asynchronous function to synchronous since group_add is async but you're calling it from a sync context        

        # self.channel_layer.group_add - The method that adds a channel to a group
        # self.room_group_name - The name of the group (like "chat_room_123")
        # self.channel_name - The unique identifier for this specific WebSocket connection


        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        # send the user list to the newly joined user
        # this will retrieve usernames from all online users

        # self.send() - WebSocket method that sends data to the connected client
        # json.dumps() - Converts a Python dictionary to a JSON string
        # 'type': 'user_list' - Message type identifier so the frontend knows how to handle this data

        # What the client receives:
        # json{
        #     "type": "user_list",
        #     "users": ["alice", "bob", "charlie"]
        # }
        self.send(json.dumps({
             'type': 'user_list',
             'users': [user.username for user in self.room.online.all()],
        }))

        if self.user.is_authenticated:
            # create a user inbox for private messages
            async_to_sync(self.channel_layer.group_add)(
                self.user_inbox,
                self.channel_name
            )
            # send the join event to the room
            async_to_sync(self.channel_layer.group_send)(
                 self.room_group_name,
                 {
                      'type': 'user_join',
                      'user': self.user.username,
                 }
            )
            self.room.online.add(self.user)



    def disconnect(self, close_code):
        # we removed the user from the channel layer group

        # It removes the current WebSocket consumer instance from a named group so it will no longer receive broadcast messages sent to that group.
        # async_to_sync() - Converts the asynchronous group_discard method to synchronous

        # self.channel_layer.group_discard - The method that removes a channel from a group
        # self.room_group_name - The name of the group to leave (like "chat_room_123")
        # self.channel_name - The unique identifier for this specific WebSocket connection

        # Why it's important: Without calling group_discard, the channel layer would keep trying to 
        # send messages to a disconnected WebSocket, which could cause memory leaks and unnecessary processing.
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
        if self.user.is_authenticated:
             # delete the user inbox for private messages
             async_to_sync(self.channel_layer.group_discard)(
                 self.user_inbox,
                 self.channel_name
             )
             # send the leave event to the room
             async_to_sync(self.channel_layer.group_send)(
                  self.room_group_name,
                  {
                       'type': 'user_leave',
                       'user': self.user.username
                  }
             )
             self.room.online.remove(self.user)

    def receive(self, text_data=None, bytes_data=None):
        # we parsed the data to JSON and extracted the message. 
        # Then, we forwarded the message using group_send to chat_message.


        # When using channel layer's group_send, your consumer has to have a method 
        # for every JSON message type you use. In our situation, type is equaled to chat_message. 
        # Thus, we added a method called chat_message.

        # If you use dots in your message types, Channels will automatically convert them 
        # to underscores when looking for a method 
        # => chat.message will become chat_message.

        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        if not self.user.is_authenticated :
                return

        if message.startswith('/pm'):
            split = message.split(' ', 2)
            target = split[1]
            target_msg = split[2]
            # send the private message to the target
            async_to_sync(self.channel_layer.group_send)(
                f'inbox_{target}',
                {
                    'type': 'private_message',
                    'user': self.user.username,
                    'message': target_msg
                }
            )
            # send the private message delivered to the user
            self.send(json.dumps({
                'type': 'private_message_delivered',
                'target': target,
                'message': target_msg
            }))
            return

        #send chat message event to the room
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'user': self.user.username,
                'message': message
            }
        )
        # print(message)
        
        Message.objects.create(user=self.user, room=self.room, content=message)



    
    # This is a message handler method in a Django Channels WebSocket consumer that receives and forwards 
    # messages from the channel layer to the connected WebSocket client.
    # 
    # Purpose: When another part of your application sends a message to the channel group using group_send(), 
    # this method receives that message and forwards it to the WebSocket client.
    
    # event is a dictionary containing the message data sent via group_send()
    def chat_message(self, event):
        # event = {
        #     'type': 'chat_message',
        #     'username': 'm.boukhit', 
        #     'message': 'Hello everyone!'
        # }
        self.send(text_data=json.dumps(event))

    def user_join(self, event):
        self.send(text_data=json.dumps(event))

    def user_leave(self, event):
        self.send(text_data=json.dumps(event))
    
    def private_message(self, event):
        self.send(text_data=json.dumps(event))        
