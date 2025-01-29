import argparse
import json
import re
from datetime import datetime
import subprocess

parser = argparse.ArgumentParser(
    prog="SaveDMs Pager",
    description="Format saved DMs for viewing in a terminal pager.",
    epilog="Save your DMs, do random stuff with them.",
)
parser.add_argument("filename", help="JSON file of the saved DMs.")
parser.add_argument(
    "-t",
    "--time",
    action="store_true",
    help="Adds send times to the start of each message.",
)
parser.add_argument(
    "-T",
    "--time_format",
    type=str,
    default="%R",
    help="If --time is enabled, sets the time format. Defaults to '%%R'",
)
parser.add_argument(
    "-d",
    "--day",
    action="store_true",
    help="Shows dividers between different days in the message thread.",
)
parser.add_argument(
    "-D",
    "--day_format",
    type=str,
    default="%A, %B %e, %Y",
    help="If --day is enabled, sets the day format. Defaults to '%%A, %%B %%e, %%Y'",
)
parser.add_argument(
    "-c",
    "--color",
    action="store_true",
    help="Adds colors to some markdown and headers.",
)
parser.add_argument(
    "-n",
    "--name",
    action="append",
    help="Names in the format username=friendly for conversion.",
    default=[],
)
parser.add_argument(
    "-a",
    "--attachments",
    action="store_true",
    help="Add links to attachments beneath messages.",
)

args = parser.parse_args()

friendly_names = {name.split("=")[0]: name.split("=")[1] for name in args.name}


class ANSI:
    HEADER = "\033[95m" if args.color else ""
    OKBLUE = "\033[94m" if args.color else ""
    OKCYAN = "\033[96m" if args.color else ""
    OKGREEN = "\033[92m" if args.color else ""
    WARNING = "\033[93m" if args.color else ""
    FAIL = "\033[91m" if args.color else ""
    ENDC = "\033[0m" if args.color else ""
    BOLD = "\033[1m" if args.color else ""
    ITALIC = "\033[3m" if args.color else ""
    UNDERLINE = "\033[4m" if args.color else ""

    @staticmethod
    def hyperlink(url: str, text: str):
        return f"\033]8;;{url}\033\\{text}\033]8;;\033\\" if args.color else url


with open(args.filename, encoding="utf8") as f:
    dms = json.load(f)


def get_terminal_cols():
    output = subprocess.check_output(["stty", "size"]).decode("utf-8")
    return int(output.split()[1])


columns = get_terminal_cols()
"""
for message in dms["messages"]:
    if len(message["attachments"]) > 0:
        print(message["attachments"][0])
        exit()
"""

last_timestamp = None
for message in dms["messages"]:
    username = message["author"]["username"]
    name = friendly_names[username] if username in friendly_names else username
    message_text = f'{ANSI.OKCYAN}{name}:{ANSI.ENDC} {message["content"]}'

    message_time_utc = datetime.fromisoformat(message["timestamp"])
    message_time_local = message_time_utc.astimezone()

    if args.time:
        message_text = f"{message_time_local.strftime(args.time_format)} {message_text}"

    message_text = re.sub(
        r"(?<![\\*])(\*{1})(?!\*)(.+?)(?<!\*)(\*|$)",
        ANSI.ITALIC + r"\2" + ANSI.ENDC,
        message_text,
        flags=re.MULTILINE,
    )  # Italicize markdown *
    message_text = re.sub(
        r"(?<!\\)(\*\*)(.+?)(?<!\\)(\*\*|$)",
        ANSI.BOLD + r"\2" + ANSI.ENDC,
        message_text,
        flags=re.MULTILINE,
    )  # Bold markdown **
    bf = message_text

    message_text = re.sub(
        r"https?://[a-z0-9.]+\.[a-z0-9]{2,}(/|\b)([A-Za-z0-9-._~:/?#\[\]@!$&'()*+,;%=]+)",
        ANSI.OKCYAN + r"\g<0>" + ANSI.ENDC,
        message_text,
    )

    message_text += ANSI.ENDC  # Append this to avoid any overflowing colors

    if args.day and (
        last_timestamp is None or last_timestamp.day != message_time_local.day
    ):
        print(
            ("\n" if last_timestamp is not None else "")
            + ANSI.HEADER
            + f" {message_time_utc.strftime(args.day_format)} ".center(columns - 1, "-")
            + ANSI.ENDC
            + "\n"
        )

    if args.attachments and len(message["attachments"]) > 0:
        for attachment in message["attachments"]:
            message_text += f"\n- {ANSI.OKGREEN}{ANSI.hyperlink(attachment['url'].replace('cdn.discordapp.com', 'fixcdn.hyonsu.com'), attachment['filename'])}"

    last_timestamp = message_time_local

    print(message_text)
