import itertools
import sys
import json
import os
import re
from pathlib import Path
from time import sleep
from tqdm import tqdm
import requests
from requests.adapters import HTTPAdapter, Retry
from datetime import datetime

from utils import group

if not sys.argv[1]:
    print("error: no messages supplied.")
    sys.exit(1)

if not sys.argv[2]:
    print("error: no token supplied.")
    sys.exit(1)

with open(sys.argv[1], encoding="utf8") as f:
    dms = json.load(f)


images_dir = re.sub(r"^[\w.\-]*", "attachments", Path(sys.argv[1]).with_suffix("").name)
os.makedirs(images_dir, exist_ok=True)

sess = requests.Session()
retries = Retry(
    total=10,
    backoff_factor=0.5, # type: ignore
    status_forcelist=[429,500,502,503,504]
)
sess.mount("http://", HTTPAdapter(max_retries=retries))

def get_attachment_path(attachment, message) -> Path:
    timestamp = datetime.fromisoformat(message["timestamp"])
    # Assuming the last 50 characters of the file name will be enough to never go too long.
    file_path = Path(images_dir).joinpath(f"{timestamp.date()}-[{attachment['id']}]-{attachment['filename'][-50:]}")
    return file_path

def refresh_attachment_url(urls: list[str], token: str) -> list[str]:
    refreshed_urls = []

    for g in tqdm(group(urls, 50), desc="Refreshing URLs"):
        res = sess.post("https://discord.com/api/v9/attachments/refresh-urls", json={
            "attachment_urls": g
        }, headers={
            "Content-Type": "application/json",
            "authorization": token
        })
        refreshed_urls = refreshed_urls + list(urls["refreshed"] for urls in res.json()["refreshed_urls"])
        sleep(0.3)
    return refreshed_urls

token = sys.argv[2]
attachments = list(itertools.chain(*[[{"attachment": attachment, "path": get_attachment_path(attachment, message), "url": attachment["url"]} for attachment in message["attachments"]] for message in dms["messages"]]))
attachment_urls = [a["url"] for a in attachments]
refreshed_attachment_urls = refresh_attachment_url(attachment_urls, sys.argv[2])


for idx, attachment in enumerate(tqdm(attachments, desc="Images")):
    url = refreshed_attachment_urls[idx]
    file_path = attachment["path"]

    if file_path.exists():
        print(f"Already downloaded {url}")
        continue

    try:
        res = sess.get(url)
        res.raise_for_status()
        with open(file_path, "wb") as f:
            f.write(res.content)
    except requests.RequestException as e:
        print(f"Error downloading {url} to {file_path}")
        print(e)



