from django.urls import re_path
from apps.tracking import consumers

websocket_urlpatterns = [
    re_path(r'^ws/tracking/order/(?P<freight_order_id>[^/]+)/$', consumers.OrderTrackingConsumer.as_asgi()),
    re_path(r'^ws/customer/(?P<customer_id>[^/]+)/$', consumers.CustomerConsumer.as_asgi()),
    re_path(r'^ws/driver/(?P<driver_id>[^/]+)/$', consumers.DriverConsumer.as_asgi()),
    re_path(r'^ws/admin/operations/$', consumers.AdminOperationsConsumer.as_asgi()),
]
