import redis.asyncio as redis
from django.conf import settings

REDIS_URL = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"
redis_client = redis.from_url(REDIS_URL, decode_responses=True)


class RoomService:
    """
    Service class for managing game rooms in Redis.
    Handles joining, leaving, retrieving users, and starting games.
    """

    @staticmethod
    def get_keys(room_code):
        """Return Redis keys for room and its users set."""
        room_key = f"room:{room_code}"
        return room_key, f"{room_key}:users"

    @classmethod
    async def join_room(cls, room_code, username):
        """Add a user to a room. Return True if joined, False if room doesn't exist or is playing."""
        room_key, users_key = cls.get_keys(room_code)
        room_data = await redis_client.hgetall(room_key)
        if not room_data or room_data.get("status") == "playing":
            return False

        async with redis_client.pipeline(transaction=True) as pipe:
            await pipe.sadd(users_key, username)
            await pipe.expire(room_key, 3600)
            await pipe.expire(users_key, 3600)
            await pipe.execute()
        return True

    @classmethod
    async def leave_room(cls, room_code, username):
        """
        Remove a user from a room.
        Return True if room still exists, False if it was deleted (empty).
        """
        room_key, users_key = cls.get_keys(room_code)
        status = await redis_client.hget(room_key, "status")

        if status != "playing":
            async with redis_client.pipeline(transaction=True) as pipe:
                await pipe.srem(users_key, username)
                await pipe.scard(users_key)
                results = await pipe.execute()

                remaining_users = results[1]
                if remaining_users == 0:
                    await redis_client.delete(room_key, users_key)
                    return False

        return True

    @classmethod
    async def get_users(cls, room_code):
        """Return a list of usernames in the room."""
        _, users_key = cls.get_keys(room_code)
        users = await redis_client.smembers(users_key)
        return list(users)

    @classmethod
    async def try_start_game(cls, room_code, username):
        """Set room status to 'playing' if user is owner. Return True if started."""
        room_key, _ = cls.get_keys(room_code)
        owner = await redis_client.hget(room_key, "owner")

        if owner == username:
            await redis_client.hset(room_key, "status", "playing")
            return True
        return False