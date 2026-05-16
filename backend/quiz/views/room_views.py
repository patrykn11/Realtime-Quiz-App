import random
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from quiz.models import Quiz
from quiz.redis_client import redis_client

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_room(request):
    login = request.user.username
    quiz_name = request.data.get("quiz_name")

    if not Quiz.objects.filter(name=quiz_name).exists():
        return Response({"error": "Quiz does not exist"}, status=404)
    
    while True:
        room_code = ''.join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=5))
        if not redis_client.exists(f"room:{room_code}"):
            break

    redis_client.hset(f"room:{room_code}", mapping={
        "owner": login,
        "status": "waiting",
        "quiz_name": quiz_name
    })

    room_data = redis_client.hgetall(f"room:{room_code}")

    return Response({
        "room_code": room_code,
        "status": "ok"
    })
