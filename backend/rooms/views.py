import random

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.redis import redis_client

from .serializers import RoomCreateSerializer


class CreateRoomAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RoomCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        quiz = serializer.validated_data["quiz"]

        while True:
            room_code = "".join(
                random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=5)
            )
            if not redis_client.exists(f"room:{room_code}"):
                break

        redis_client.hset(
            f"room:{room_code}",
            mapping={
                "owner": request.user.username,
                "status": "waiting",
                "quiz_id": quiz.id,
                "quiz_name": quiz.name,
            },
        )
        return Response({"room_code": room_code, "status": "ok"})
