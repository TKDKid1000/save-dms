import asyncio
import math
from urllib.parse import urlencode
import httpx

import requests
from tqdm import tqdm


async def async_range(start: int, end: int):
    """
    Asynchronous range function.
    """
    for i in range(start, end):
        yield i
        await asyncio.sleep(0)


def download_messages_loop(
    token: str, total_messages: int, channel_id: str, limit: int
) -> list[dict]:
    messages = []
    discord_limit = min(limit, 100)  # The built in API limit of messages per query

    for _ in tqdm(range(0, math.ceil(total_messages / discord_limit))):
        query_params = {"limit": discord_limit}
        if len(messages) > 0:
            query_params["before"] = messages[0]["id"]

        new_messages = requests.get(
            f"https://discord.com/api/v9/channels/{channel_id}/messages?{urlencode(query_params)}",
            headers={"authorization": token},
            timeout=10,
        ).json()

        for new_message in new_messages:
            messages.insert(0, new_message)
            # bar.goto(len(messages))

    return messages

async def async_download_messages_loop(
    token: str, total_messages: int, channel_id: str, limit: int
) -> list[dict]:
    messages = []
    discord_limit = min(limit, 100)  # The built in API limit of messages per query

    async for _ in async_range(0, math.ceil(total_messages / discord_limit)):
        query_params = {"limit": discord_limit}
        if len(messages) > 0:
            query_params["before"] = messages[0]["id"]

        async with httpx.AsyncClient() as session:
            new_messages = await session.get(
                f"https://discord.com/api/v9/channels/{channel_id}/messages?{urlencode(query_params)}",
                headers={"authorization": token},
                timeout=10,
            )
            new_messages = new_messages.json()

        for new_message in new_messages:
            messages.insert(0, new_message)
            # bar.goto(len(messages))

    return messages
