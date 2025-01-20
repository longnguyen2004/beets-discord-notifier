from beets.plugins import BeetsPlugin
from beets.library import Library, Album
from typing import cast
from pathlib import Path
import requests
import re
import json

markdown_format_regex = re.compile(r"([\\*_])")


def escape_markdown(s: str):
    return markdown_format_regex.sub(r"\\\g<1>", s)


class DiscordNotifier(BeetsPlugin):
    def __init__(self):
        super().__init__(name="discord")
        self.config.add({
            "url": ""
        })
        self.register_listener("album_imported", self.send_message)
        self.webhook_url = cast(str, self.config["url"].as_str())
        if (len(self.webhook_url) == 0):
            raise ValueError("Webhook URL cannot be empty, please specify the URL")

    def send_message(self, lib: Library, album: Album):
        body = {}
        message = {
            "content": "# New album",
            "embeds": [
                {
                    "fields": [
                        {
                            "name": "Title",
                            "value": escape_markdown(album["album"]),
                        },
                        {
                            "name": "Artist",
                            "value": escape_markdown(album["albumartist"])
                        },
                        {
                            "name": "Track count",
                            "value": album["albumtotal"]
                        }
                    ]
                }
            ]
        }
        cover_path = album.artpath
        if (cover_path is not None):
            cover_path = Path(cover_path.decode())  # We pretend it's UTF-8
            file_name = cover_path.name
            body["files[0]"] = (file_name, open(cover_path, mode='rb').read())
            message["embeds"][0]["thumbnail"] = {
                "url": f"attachment://{file_name}"
            }
        body["payload_json"] = (None, json.dumps(message))
        requests.post(self.webhook_url, files=body)
