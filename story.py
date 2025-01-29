import asyncio
import json
import sys

from tqdm import tqdm
from utils import group, join_grammatically
from openai import AsyncOpenAI
import os
from pathlib import Path
import re
from dotenv import load_dotenv
from textwrap import dedent

load_dotenv()

openai = AsyncOpenAI(
    api_key=os.environ["DEEPINFRA_API_KEY"],
    base_url="https://api.deepinfra.com/v1/openai",
)

if not sys.argv[1]:
    print("error: no summary supplied.")
    sys.exit(1)

with open(sys.argv[1], encoding="utf8") as f:
    summary = f.read()

names, summary = summary.split("\n", 1) # type: ignore
names: dict[str, str] = dict(json.loads(names)) # type: ignore

MODEL = "meta-llama/Llama-3.3-70B-Instruct-Turbo"

async def main():
    conversation_segments = group(summary.split("\n\n"), 20) # Magic number, make this configurable
    story_segments: list[str] = []

    for conv_segment in tqdm(conversation_segments):
        conv_summary = "".join(conv_segment)
        if len(story_segments) > 0:
            response = await openai.chat.completions.create(
                model=MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": dedent(f"""The following is the previous section of a story between {join_grammatically(list(names.values()))}:
                        {story_segments[-1]}

                        What follows is a summary of the next section of the story:
                        {conv_summary}
                        Continue the story, including proper transitions, in third person, from the summary. Use creative language. Do not finish the story or deviate from the summary:"""),
                    }
                ],
                max_tokens=100000,
            )
        else:
            response = await openai.chat.completions.create(
                model=MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": dedent(f"""Write the beginning of a story between {join_grammatically(list(names.values()))}:
                        What follows is a summary of the first part of the story: 
                        {conv_summary}
                        Rewrite this segment of the story in third person, only as an introduction. Use creative language. Do not finish the story or deviate from the summary:"""),
                    }
                ],
                max_tokens=100000,
            )

        segment = response.choices[0].message.content or ""
        if segment:
            story_segments.append(segment)


    story = "".join(story_segments)

    with open(
        re.sub(r"^[\w.\-]*", "story", Path(sys.argv[1]).with_suffix(".txt").name),
        "w",
        encoding="utf8",
    ) as f:
        f.write(story)

asyncio.run(main())
