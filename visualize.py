import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from time import localtime

import dominate
from dominate.tags import div, img, meta, span, style
from dominate.util import raw

if not sys.argv[1]:
    print("error: no messages supplied.")
    sys.exit(1)

with open(sys.argv[1], encoding="utf8") as f:
    dms = json.load(f)

doc = dominate.document(
    title=dms["channel"]["name"] + " | " + dms["channel"]["type"].capitalize()
)


with doc.head:
    style(
        raw(
            """@import url("https://fonts.googleapis.com/css2?family=Roboto&display=swap");"""
        )
    )
    style(
        raw(
            """*{font-family:"Roboto", sans-serif}body{margin:0}.messages{box-sizing:border-box;padding-bottom:20px;display:flex;flex:1;flex-direction:column}.message{color:white;background:#36393f;user-select:text;-moz-user-select:text;display:flex;flex-direction:row;padding:5px 10px}.message .messagewrapper{display:flex;align-items:center;flex-direction:row}.message .hoverdate{min-width:50px;font-size:10px;color:gray;visibility:hidden}.message:hover .hoverdate{visibility:visible}.message .contentwrapper{display:block}.message .contentwrapper .content{white-space:pre-wrap;display:block;overflow-wrap:normal;word-break:normal}.message .contentwrapper .content p{margin:0}.message .avatar{width:40px;height:40px;border-radius:50%;margin-right:10px;vertical-align:top;cursor:pointer;background:#8f8e8e}.message .avatar:active{transform:translateY(2px)}.message .user{font-weight:bold;cursor:pointer}.message .user:hover{filter: brightness(90%)}.message .date{font-size:12px;color:gray;margin-left:5px}.message:hover{background-color:#34373c}.separator{display:flex;align-items:center;text-align:center;padding-top:10px;padding-bottom:10px;background:#36393f;color:gray}.separator::after,.separator::before{content:"";flex:1;border-bottom:1px solid gray}.separator:not(:empty)::after,.separator:not(:empty)::before{margin:10px 0}"""
        )
    )
    meta(charset="UTF-8")


def author_name(author):
    """Returns global name or username of a message author."""
    global_name = author.get("global_name")
    return global_name if global_name else author["username"]


def avatar_url(author):
    """Returns avatar url of a message author."""
    return f"https://cdn.discordapp.com/avatars/{author['id']}/{author['avatar']}"


with doc:
    with div(cls="messages"):
        for index, message in enumerate(dms["messages"]):
            show_separator = index != 0 and (
                datetime.fromisoformat(message["timestamp"]).day
                != datetime.fromisoformat(dms["messages"][index - 1]["timestamp"]).day
                or datetime.fromisoformat(message["timestamp"])
                > datetime.fromisoformat(dms["messages"][index - 1]["timestamp"])
                + timedelta(days=1)
            )
            show_avatar = (
                index == 0
                or message["author"]["id"] != dms["messages"][index - 1]["author"]["id"]
                or show_separator
            )
            reply = message.get("referenced_message")

            tzinfo = datetime.now(timezone.utc).astimezone().tzinfo
            date = datetime.fromisoformat(message["timestamp"]).astimezone(tzinfo)

            date = date + timedelta(
                hours=date.hour - localtime().tm_isdst
            )  # Murky DST patch, but it works.

            if show_separator:
                div(date.strftime("%B %d, %Y"), cls="separator")
            with div(cls="message"):
                if show_avatar:
                    img(src=avatar_url(message["author"]), cls="avatar")
                    with div():
                        span(author_name(message["author"]), cls="user")
                        span(date.strftime("%Y-%m-%d %I:%M %p"), cls="date")
                        with div(cls="messagewrapper"):
                            with div(cls="contentwrapper"):
                                div(
                                    message["content"], cls="content"
                                )  # Format as markdown.
                else:
                    with div(cls="messagewrapper"):
                        div(date.strftime("%I:%M %p"), cls="hoverdate")
                        with div(cls="contentwrapper"):
                            div(
                                message["content"], cls="content"
                            )  # Format as markdown.

with open(Path(sys.argv[1]).with_suffix(".html"), "w", encoding="utf8") as f:
    f.write(str(doc))
