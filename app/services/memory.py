import json

from redis.asyncio import Redis

from app.core.config import get_settings

settings = get_settings()

_redis = Redis.from_url(settings.redis_url, decode_responses=True)

MAX_HISTORY_TURNS = 10  # keep last 10 exchanges to bound prompt size
TTL_SECONDS = 60 * 60 * 24  # sessions expire after 24h of inactivity


def _key(session_id: str) -> str:
    return f"chat:history:{session_id}"


async def get_history(session_id: str) -> list[dict[str, str]]:
    """Fetch stored turns for a session, oldest first."""
    raw = await _redis.lrange(_key(session_id), 0, -1)
    return [json.loads(item) for item in raw]


async def append_turn(session_id: str, role: str, content: str) -> None:
    """Append one turn (user or assistant message) to the session's history."""
    key = _key(session_id)
    await _redis.rpush(key, json.dumps({"role": role, "content": content}))
    await _redis.ltrim(key, -MAX_HISTORY_TURNS * 2, -1)  # *2: user+assistant pairs
    await _redis.expire(key, TTL_SECONDS)