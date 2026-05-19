from common.redis import async_redis_client as redis_client


class RoomService:
    """Manage lobby room state in Redis."""

    ROOM_TTL = 3600

    @staticmethod
    def get_keys(room_code):
        room_key = f"room:{room_code}"
        return room_key, f"{room_key}:users"

    @classmethod
    async def join_room(cls, room_code, username):
        room_key, users_key = cls.get_keys(room_code)
        room_data = await redis_client.hgetall(room_key)
        if not room_data or room_data.get("status") == "playing":
            return False

        async with redis_client.pipeline(transaction=True) as pipe:
            await pipe.sadd(users_key, username)
            await pipe.expire(room_key, cls.ROOM_TTL)
            await pipe.expire(users_key, cls.ROOM_TTL)
            await pipe.execute()
        return True

    @classmethod
    async def leave_room(cls, room_code, username):
        room_key, users_key = cls.get_keys(room_code)
        status = await redis_client.hget(room_key, "status")

        if status != "playing":
            async with redis_client.pipeline(transaction=True) as pipe:
                await pipe.srem(users_key, username)
                await pipe.scard(users_key)
                results = await pipe.execute()

            if results[1] == 0:
                await redis_client.delete(room_key, users_key)
                return False

        return True

    @classmethod
    async def get_users(cls, room_code):
        _, users_key = cls.get_keys(room_code)
        return list(await redis_client.smembers(users_key))

    @classmethod
    async def try_start_game(cls, room_code, username):
        room_key, _ = cls.get_keys(room_code)
        if await redis_client.hget(room_key, "owner") == username:
            await redis_client.hset(room_key, "status", "playing")
            return True
        return False
