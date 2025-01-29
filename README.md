# Save Discord DMs

A collection of tools to save, analyze, and relive your past Discord messages.

## Downloading

The entire program is split into several files, one for each medium of messaging. They'll be consolidated at some point, but for now, they are split into these files:

- `download_dms.py`
- `download_guilds.py`

The former is used for DMs and group chats, while the latter is good for servers/guilds. The reason they are split apart is because guilds have to scan through multiple channels, as well as downloading all the metadata and active members from the guild. Of course, this only downloads messages from channels that you have access to, but it downloads every channel nonetheless.

To use this tool, you will need to find your Discord account token. This repository is NOT a tool designed for this, so I link to [this StackOverflow post](https://stackoverflow.com/questions/67348339/any-way-to-get-my-discord-token-from-browser-dev-console), which mentions several methods of doing this. Obviously, don't share your account token; that's dangerous. I recommend storing this in some environment variable to make it easier to use the next few commands, but it's up to you.

Next, clone the repository and `cd` into it using your terminal.

From here, now that you have this token, you'll need to determine which medium you want to download: DMs or a server.

### DMs and Group Chats

These are the same, and rely on the same script: `download_dms.py`. When you download these DMs, they'll wind up in the root of the repository and should probably be moved elsewhere. I keep a people/ directory and a groups/ directory open for these DMs, but you may do as you please. When the script finishes, there should be two files: `messages - username - [user id].txt` and `save-dms - username - [user id].json`. The former is a textual document containing a pure-text transcript of what you and the other person said to one another. I found this quite useful for both rereading and embedding. The JSON format contains everything stored about every message, so it is very large, but it also allows you to know basically everything about the message (date sent/edited, attachments, reactions, etc.), so you can use this for more advanced things, such as [[visualizing your past messages]].

How do you obtain this channel id, you might ask? Simple! First, make sure you have developer tools enabled in Discord settings, which will add a few extra things to your right click context menu. Then, right click on the user/group in your DMs list and click "Copy Channel ID".

The command to use has several arguments:

```
usage: SaveDMs [-h] -t TOKEN -c CHANNEL [-l LIMIT]

options:
  -h, --help            show this help message and exit
  -t TOKEN, --token TOKEN
                        Your user account token.
  -c CHANNEL, --channel CHANNEL
                        The channel id, NOT the user id, that will be downloaded.
  -l LIMIT, --limit LIMIT
                        Maximum number of messages to download, starting from the end. Defaults to all.

Save your DMs, do random stuff with them.
```

### Guilds

The process for guilds is almost exactly the same, only the inputs and outputs vary in a few small ways. For guilds, you will need to supply the guild id, which is obtaining in the same way as the channel id in the previous method, but you must instead right click on the guild/server's icon on the left sidebar. You may also specify a channel id to this command, which will limit the download to only that channel, as well as the other assorted server metadata.

As an output, you will get a new directory, titled, `save-dms-guild - guild name - [guild id]`. Inside, you'll find a JSON an text file for every channel, as per the established naming convention, as well as an `active_members.json` file and a `metadata.json` file. The former contains the user information of everyone who has ever posted a message to the server, and the latter contains all accessible server metadata that Discord stores. The content of the latter varies depending on your permissions in the server.

Here is the command's arguments:

```
usage: SaveDMs-Guild [-h] -t TOKEN -g GUILD [-c CHANNEL] [-l LIMIT]

options:
  -h, --help            show this help message and exit
  -t TOKEN, --token TOKEN
                        Your user account token.
  -g GUILD, --guild GUILD
                        The guild id to be downloaded.
  -c CHANNEL, --channel CHANNEL
                        The channel id to be downloaded, if only downloading a single channel.
  -l LIMIT, --limit LIMIT
                        Maximum number of messages to download, per channel, starting from the end. Defaults to all.
```

## Analysis

I'm working on this :'(. Just give it time and I'll get some sweet analysis tools done. The most functional tool right now is `summarize.py`, which takes the JSON file of your message history, splits it into 4 hour increments (conversations), and then sends it of to an AI which summaries the individual conversations, allowing you to easily reread and analyze past conversations. This can also be used for efficiently chunking and embedding messages.

## Reliving

Well, this is what I made the tool for, really. You can actively relive your messages, if you want, by using any number of different things. If the summary is enough for you, use that! If not, you can run your messages's JSON file through `visualize.py`, which will output a complete messaging history in HTML format, complete with Discord-like CSS and everything, allowing you to, mostly, relive the entire chat as if it was happening right then and there.

Another WIP tool is `story.py`, which will write a complete and accurate story about what the hell happened in those DMs.

In general, the `story.py` system works; it's just incredibly slow. I'll work on parellelizing it eventually, but since it generates the story in segments that rely on the prior, it becomes difficult to parallelize due to the necessity of sequential processing. This program will, after the amount of time it takes to finish - around 2:30s for a 5000 message thread, utilizing DeepInfra's LLM hardware - output a complete story of the chat history. It's pretty contextually accurate, but it puts a spin on things a bit by describing everything from a third-person perspective - one you likely didn't get when first creating those messages - and utilizing creative diction.

It's still a work in progress, as stated, and things like providing contextual information like message dates/times will certainly be added in the future. For now, however, it will provide a decent afternoon (or full day, depending on your conversation length) read that should help you see what you missed.

## Context

I created this tool a long time ago after finding a similar C# based system for backing up Discord messages, which I really quite liked. However, C# was a pain to run and automate, so I decided to create my own backup system in Python. I started using it to save every single DM or group chat that I ever closed, so that I could look back on it after I inevitably had to go.

Since then, I have undergone a lot of changes in my life, and having this tool was a great way to remember the good parts of some of my online relationships. I have kept it private for the time being because it is absolutely not polished and kind of sucks, but it works well enough for me, and I figured I would release it in case other people wanted to relive some of their favorite online memories.

Nowadays, I save every single DM channel, server, and group chat that I am ever part of because you never know when something might randomly happen to it. (The support for servers was added after a tragic incident...) If you're a fellow data hoarder, maybe you'll wish to do the same.

## License

Uhh, MIT.
