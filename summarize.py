import asyncio
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

load_dotenv()

openai = AsyncOpenAI(
    api_key=os.environ["DEEPINFRA_API_KEY"],
    base_url="https://api.deepinfra.com/v1/openai",
)


T = TypeVar("T")


def group(array: list[T], size: int) -> list[list[T]]:
    """
    Groups the elements of an array into sublists of a specified size.

    Args:
    1. array: A list of elements to be grouped.
    2. size: The desired size of each sublist.

    Returns:
    A list of sublists, where each sublist contains at most `size` elements.
    """
    return [array[i : i + size] for i in range(0, len(array), size)]


def join_grammatically(words: list[str]) -> str:
    if len(words) == 0:
        return ""
    elif len(words) == 1:
        return words[0]
    else:
        return ", ".join(words[:-1]) + " and " + words[-1]


async def summarize(text: str) -> str:
    """Summarizes the provided text."""
    response = await openai.chat.completions.create(
        model="mistralai/Mistral-7B-Instruct-v0.3",
        messages=[
            {
                "role": "user",
                "content": "Summarize the following conversation into a several bullet points. Include all significant conversation elements:\n"
                + text,
            }
        ],
        max_tokens=1024,
    )

    return response.choices[0].message.content or ""


if not sys.argv[1]:
    print("error: no messages supplied.")
    sys.exit(1)

names = {
    name.partition("=")[0]: name.partition("=")[2]
    for name in sys.argv[2:]
    if "=" in name
}

with open(sys.argv[1], encoding="utf8") as f:
    dms = json.load(f)
conversations: list[str] = []

last_timestamp: datetime = datetime(2000, 1, 1)
for message in tqdm(dms["messages"], desc="Conversations"):
    timestamp = datetime.fromisoformat(message["timestamp"])
    formatted_message = (
        names[message["author"]["username"]] + ": " + message["content"] + "\n"
    )
    if timestamp.timestamp() < (last_timestamp + timedelta(hours=4)).timestamp():
        conversations[-1] += formatted_message
    else:
        conversations.append(formatted_message)
    last_timestamp = timestamp


# Group conversations into groups of 100, then run those groups in parallel with async.
async def main():
    summaries: list[str] = []

    groups = group(conversations, 200)
    print(len(groups))

    for conversation_group in tqdm(groups, desc="Summaries"):
        group_summaries = await atqdm.gather(
            *[summarize(conversation) for conversation in conversation_group]
        )

        summaries.extend(group_summaries)

    summary = "\n\n".join(summaries)

    with open(
        re.sub(r"^[\w.\-]*", "summary", Path(sys.argv[1]).with_suffix(".txt").name),
        "w",
        encoding="utf8",
    ) as f:
        f.write(summary)

    print("Summarization finished, writing story.")
    response = await openai.chat.completions.create(
        model="mistralai/Mistral-7B-Instruct-v0.3",
        messages=[
            {
                "role": "user",
                "content": f"""The following input is a summary of several conversations between {join_grammatically(list(names.values()))}.
                Rewrite this summary as a story from a third person perspective.\n:{summary}""",
            }
        ],
        max_tokens=100000,
    )

    story = response.choices[0].message.content or ""

    with open(
        re.sub(r"^[\w.\-]*", "story", Path(sys.argv[1]).with_suffix(".txt").name),
        "w",
        encoding="utf8",
    ) as f:
        f.write(story)


asyncio.run(main())
