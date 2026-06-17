import json
from channels.generic.websocket import JsonWebsocketConsumer
from asgiref.sync import async_to_sync

class OrderTrackingConsumer(JsonWebsocketConsumer):
    """
    Consumer that broadcasts real-time position updates to anyone listening to a specific FreightOrder.
    """
    def connect(self):
        self.freight_order_id = self.scope['url_route']['kwargs']['freight_order_id']
        self.group_name = f"tracking_order_{self.freight_order_id}"

        # Join order tracking group
        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        # Leave group
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )

    def receive_json(self, content):
        pass

    def location_update(self, event):
        # Send event to WebSocket client
        self.send_json({
            "type": "location_update",
            "freight_order_id": event["freight_order_id"],
            "latitude": event["latitude"],
            "longitude": event["longitude"],
            "speed": event["speed"],
            "heading": event["heading"],
            "status": event["status"],
            "eta": event["eta"]
        })

class CustomerConsumer(JsonWebsocketConsumer):
    """
    Consumer that keeps active clients updated on any status change of their orders.
    """
    def connect(self):
        self.customer_id = self.scope['url_route']['kwargs']['customer_id']
        self.group_name = f"customer_{self.customer_id}"

        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )

    def order_update(self, event):
        self.send_json({
            "type": "order_update",
            "freight_order_id": event["freight_order_id"],
            "status": event["status"],
            "eta": event["eta"]
        })

class DriverConsumer(JsonWebsocketConsumer):
    """
    Consumer that lets active online drivers receive notifications and match invitations.
    """
    def connect(self):
        self.driver_id = self.scope['url_route']['kwargs']['driver_id']
        self.group_name = f"driver_{self.driver_id}"

        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )

    def matching_invite(self, event):
        self.send_json({
            "type": "matching_invite",
            "freight_order_id": event["freight_order_id"],
            "pickup_distance": event["pickup_distance"],
            "compatibility_score": event["compatibility_score"]
        })

class AdminOperationsConsumer(JsonWebsocketConsumer):
    """
    Consumer that allows operational and admin dashboards to track all active shipments.
    """
    def connect(self):
        self.group_name = "admin_operations"

        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )

    def operations_update(self, event):
        self.send_json({
            "type": "operations_update",
            "freight_order_id": event["freight_order_id"],
            "driver_name": event["driver_name"],
            "latitude": event["latitude"],
            "longitude": event["longitude"],
            "status": event["status"],
            "eta": event["eta"]
        })
