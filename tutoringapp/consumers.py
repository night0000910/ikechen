from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model

import json
import datetime
import math
import asyncio

from . import models


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        class_id = self.scope["url_route"]["kwargs"]["class_id"]
        self.room_group_name = class_id

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # 授業開始時刻をデータベースに記録する
        now_date = await asyncio.get_event_loop(None, datetime.datetime.utcnow)
        print(now_date)
        user_id = self.scope["url_route"]["kwargs"]["user_id"]
        user = get_user_model().objects.get(id=user_id)
        user.class_start_datetime = now_date
        user.save()
    
    async def disconnect(self, close_code):

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        print("通信が切断されました")

        # 授業開始時刻、授業時間をデータベースに記録する
        now_date = datetime.datetime.utcnow()
        user_id = self.scope["url_route"]["kwargs"]["user_id"]
        user = get_user_model().objects.get(id=user_id)
        user.class_ending_datetime = now_date
        time_interval = user.class_ending_datetime - user.class_start_datetime
        user.spent_time += math.floor(time_interval.seconds/60)
        user.save()

    async def receive(self, text_data):

        receive_dict = json.loads(text_data)
        message = receive_dict["message"]
        action = receive_dict["action"]

        if (action == "new-offer") or (action == "new-answer"):
            receiver_channel_name = receive_dict["message"]["receiver_channel_name"]

            receive_dict["message"]["receiver_channel_name"] = self.channel_name

            await self.channel_layer.send(
                receiver_channel_name,
                {
                    "type" : "send.sdp",
                    "receive_dict" : receive_dict,
                }
            )

            return
        
        receive_dict["message"]["receiver_channel_name"] = self.channel_name

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type" : "send.sdp",
                "receive_dict" : receive_dict,
            }
        )

    async def send_sdp(self, event):
        receive_dict = event["receive_dict"]

        await self.send(text_data=json.dumps(receive_dict))