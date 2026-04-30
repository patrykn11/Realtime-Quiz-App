import random
import redis
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

REDIS_URL = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_room(request):
    login = request.user.username
    while True:
        room_code = ''.join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=5))
        if not redis_client.exists(f"room:{room_code}"):
            break
    redis_client.hset(f"room:{room_code}", mapping={
        "owner": login,
        "status": "waiting"
    })

    return Response({
        "room_code": room_code,
        "status": "ok"
    })