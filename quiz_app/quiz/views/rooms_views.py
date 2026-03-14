import random
import redis
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

REDIS_URL = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_room(request):
    login = request.user.username
    r = redis.Redis.from_url(REDIS_URL)
    while True:
        room_code = ''.join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=5))
        if not r.exists(f"room:{room_code}"):
            break
    r.hset(f"room:{room_code}", mapping={
        "owner": login,
        "status": "waiting"
    })

    return Response({
        "room_code": room_code,
        "status": "ok"
    })