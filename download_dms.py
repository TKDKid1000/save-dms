import argparse
import json
import sys

import requests

from channel_types import CHANNEL_TYPES
from download_loop import download_messages_loop

parser = argparse.ArgumentParser(
    prog="SaveDMs",
    description="Download Discord DMs using a single script.",
    epilog="Save your DMs, do random stuff with them.",
)
parser.add_argument("-t", "--token", required=True, help="Your user account token.")
parser.add_argument(
    "-c",
    "--channel",
    required=True,
    help="The channel id, NOT the user id, that will be downloaded.",
)
parser.add_argument(
    "-l",
    "--limit",
    required=False,
    default=-1,
    type=int,
    help="Maximum number of messages to download, starting from the end. Defaults to all.",
)

args = parser.parse_args()

token = args.token
channel_id = args.channel
limit = 2**10000 if args.limit < 0 else args.limit

channel_response = requests.get(
    f"https://discord.com/api/v9/channels/{channel_id}",
    headers={"authorization": token},
    timeout=10,
)

if channel_response.status_code == 401:
    print("401: Unauthorized")
    sys.exit(1)
channel = channel_response.json()

channel_name = (
    channel["name"]
    if channel.get("name")
    else "|".join(
        recipient["username"] + "#" + recipient["discriminator"]
        for recipient in channel["recipients"]
    )
)

total_messages = min(
    requests.get(
        f"https://discord.com/api/v9/channels/{channel_id}/messages/search",
        headers={"authorization": token},
        timeout=10,
    ).json()["total_results"],
    limit,
)

messages = download_messages_loop(
    token=token, total_messages=total_messages, channel_id=channel_id, limit=limit
)

dms = {
    "channel": {
        "id": channel_id,
        "name": channel_name,
        "type": CHANNEL_TYPES[channel["type"]],
    },
    "recipients": channel.get("recipients"),
    "messages": messages,
    "messageCount": len(messages),  # More accurate than the estimated total_messages
}

with open(
    f"save-dms - {channel_name} - [{channel_id}].json", "w", encoding="utf8"
) as f:
    json.dump(dms, f, default=str)

with open(f"messages - {channel_name} - [{channel_id}].txt", "a", encoding="utf8") as f:
    for message in messages:
        f.write(f"""{message["author"]["username"]}: {message["content"]}\n""")
