import random
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from quiz.models import Quiz
from quiz.redis_client import redis_client


class CreateRoomAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        login = request.user.username
        quiz_name = request.data.get("quiz_name")

        if not Quiz.objects.filter(name=quiz_name).exists():
            return Response({"error": "Quiz does not exist"}, status=404)

        while True:
            room_code = ''.join(
                random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=5)
            )
            if not redis_client.exists(f"room:{room_code}"):
                break

        redis_client.hset(
            f"room:{room_code}",
            mapping={
                "owner": login,
                "status": "waiting",
                "quiz_name": quiz_name
            },
        )

        return Response({"room_code": room_code, "status": "ok"})
