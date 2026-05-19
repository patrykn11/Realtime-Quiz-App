from django.urls import path

from .views import CreateRoomAPIView


app_name = "rooms"
urlpatterns = [
    path("create_room/", CreateRoomAPIView.as_view(), name="create"),
]
