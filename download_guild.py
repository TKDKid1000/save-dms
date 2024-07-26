import argparse
import json
import os
import sys
from os import path

import requests

from channel_types import CHANNEL_TYPES
from download_loop import download_messages_loop

parser = argparse.ArgumentParser(
    prog="SaveDMs-Guild",
    description="Download Discord guilds/servers using a single script.",
    epilog="Save your guilds, do random stuff with them.",
)
parser.add_argument("-t", "--token", required=True, help="Your user account token.")
parser.add_argument(
    "-g", "--guild", required=True, help="The guild id to be downloaded."
)
parser.add_argument(
    "-c",
    "--channel",
    action="append",
    required=False,
    help="The channel id to be downloaded, if only downloading a single channel.",
)
parser.add_argument(
    "-l",
    "--limit",
    required=False,
    default=-1,
    type=int,
    help="Maximum number of messages to download, per channel, starting from the end. Defaults to all.",
)

args = parser.parse_args()

token = args.token
guild_id = args.guild
limit = 2**10000 if args.limit < 0 else args.limit

channel_ids = args.channel

guild_response = requests.get(
    f"https://discord.com/api/v9/guilds/{guild_id}",
    headers={"authorization": token},
    timeout=10,
)

if guild_response.status_code == 401:
    print("401: Unauthorized")
    sys.exit(1)

guild = guild_response.json()

channels = requests.get(
    f"https://discord.com/api/v9/guilds/{guild_id}/channels",
    headers={"authorization": token},
    timeout=10,
).json()

if channel_ids is not None:
    channels = [channel for channel in channels if channel["id"] in channel_ids]

guild_dir = f"./save-dms-guild - {guild['name']} - [{guild_id}]"
if not path.exists(guild_dir):
    os.mkdir(guild_dir)


# TODO: Save guild metadata to a "metadata.json" file in the guild directory.
with open(
    path.join(guild_dir, "metadata.json"),
    "w",
    encoding="utf8",
) as f:
    json.dump(guild, f, default=str)

members = []
member_ids = []

for channel in channels:
    channel_id = channel["id"]

    channel_name = channel["name"]

    total_messages = min(
        requests.get(
            f"https://discord.com/api/v9/guilds/{guild_id}/messages/search?channel_id={channel_id}",
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
        "messageCount": len(
            messages
        ),  # More accurate than the estimated total_messages
    }

    for message in messages:
        if message["author"]["id"] not in member_ids:
            member_ids.append(message["author"]["id"])
            members.append(message["author"])

    with open(
        path.join(guild_dir, f"save-dms - {channel_name} - [{channel_id}].json"),
        "w",
        encoding="utf8",
    ) as f:
        json.dump(dms, f, default=str)

    with open(
        path.join(guild_dir, f"messages - {channel_name} - [{channel_id}].txt"),
        "a",
        encoding="utf8",
    ) as f:
        for message in messages:
            f.write(f"""{message["author"]["username"]}: {message["content"]}\n""")

with open(
    path.join(guild_dir, "active_members.json"),
    "w",
    encoding="utf8",
) as f:
    json.dump(members, f, default=str)
