import asyncio
from collections import defaultdict
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from time import sleep
from typing import Type, TypeVar
import re
from tqdm.asyncio import tqdm as atqdm

from openai import AsyncOpenAI
from tqdm import tqdm

from dotenv import load_dotenv

from utils import group, split_conversations

load_dotenv()

openai = AsyncOpenAI(
    api_key=os.environ["DEEPINFRA_API_KEY"],
    base_url="https://api.deepinfra.com/v1/openai",
)


async def summarize(text: str) -> str:
    """Summarizes the provided text."""
    response = await openai.chat.completions.create(
        model="mistralai/Mistral-7B-Instruct-v0.3",
        messages=[
            {
                "role": "user",
                "content": "Summarize the following conversation into a several bullet points. Respond with only bullet points and no headers. Include all significant conversation elements:\n"
                + text,
            }
        ],
        max_tokens=1024,
    )

    return response.choices[0].message.content or ""


if not sys.argv[1]:
    print("error: no messages supplied.")
    sys.exit(1)

names = defaultdict(lambda: "Ghost")
names = {
    name.partition("=")[0]: name.partition("=")[2]
    for name in sys.argv[2:]
    if "=" in name
}

with open(sys.argv[1], encoding="utf8") as f:
    dms = json.load(f)

conversations = split_conversations(
    messages=dms["messages"], conversation_duration=timedelta(hours=4)
)


conversation_transcripts = [
    list(
        f'{names[message["author"]["username"]]}: {message["content"]}\n'
        for message in conversation
    )
    for conversation in conversations
]


# Group conversations into groups of 100, then run those groups in parallel with async.
async def main():
    summaries: list[str] = []

    groups = group(conversations, 200)
    print(len(groups))

    for conversation_group in tqdm(groups, desc="Summaries"):
        group_summaries = await atqdm.gather(
            *[
                summarize(
                    "".join(
                        f'{names[message["author"]["username"]]}: {message["content"]}\n'
                        for message in conversation
                    )
                )
                for conversation in conversation_group
            ]
        )

        summaries.extend(group_summaries)

    summary = "\n\n".join(summaries)
    summary = re.sub(r"^ ?(?:[*-]|\d+[.)])", "-", summary, flags=re.MULTILINE)
    summary = json.dumps(names) + "\n" + summary

    with open(
        re.sub(r"^[\w.\-]*", "summary", Path(sys.argv[1]).with_suffix(".txt").name),
        "w",
        encoding="utf8",
    ) as f:
        f.write(summary)


asyncio.run(main())
