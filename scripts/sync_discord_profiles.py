"""Manually fetch the team's public Discord identity and keep local PNG snapshots.

Uses the public lookup already used by the supplied OscarDev reference. No token,
presence, guild membership or messages. All responses are checked before writing.
"""
from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "profile"
CONFIG_PATH = PROFILE / "profile.json"
ASSETS = PROFILE / "assets"
API = "https://www.vibebot.gg/api/tools/avatar-lookup?id="


def download(url: str, limit: int) -> bytes:
    request = Request(url, headers={"User-Agent": "FlowCaribe-Profile/1.0"})
    with urlopen(request, timeout=30) as response:
        data = response.read(limit + 1)
    if len(data) > limit:
        raise ValueError("Response exceeds the allowed size")
    return data


def sync(checked_on: str) -> None:
    date.fromisoformat(checked_on)
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    originals = {}
    profiles = []
    for person in config["developers"]:
        user_id = person["discord_id"]
        if not isinstance(user_id, str) or not user_id.isdigit() or not 17 <= len(user_id) <= 20:
            raise ValueError("Invalid Discord user ID")
        source = API + user_id
        payload = json.loads(download(source, 100_000))
        user = payload["user"]
        if user.get("id") != user_id:
            raise ValueError("The lookup returned a different user")
        username = user.get("username")
        if not isinstance(username, str) or not 1 <= len(username) <= 32:
            raise ValueError("Invalid public Discord username")
        url = ((payload.get("avatar") or {}).get("png") or {}).get("256") or payload.get("defaultAvatar")
        parsed = urlsplit(url or "")
        if parsed.scheme != "https" or parsed.netloc != "cdn.discordapp.com":
            raise ValueError("Avatar must originate from Discord's official CDN")
        if not parsed.path.startswith((f"/avatars/{user_id}/", "/embed/avatars/")):
            raise ValueError("Unexpected Discord avatar path")
        data = download(url, 2_000_000)
        if not data.startswith(b"\x89PNG\r\n\x1a\n") or data[12:16] != b"IHDR":
            raise ValueError("Avatar is not a PNG")
        destination = (ASSETS / person["avatar"]).resolve()
        if not destination.is_relative_to(ASSETS / "team") or destination.suffix != ".png":
            raise ValueError("Avatar destination must be a PNG inside assets/team")
        originals[destination] = data
        person["discord_username"] = username
        profiles.append({
            "name": person["name"], "id": user_id, "username": username,
            "global_name": user.get("global_name"), "avatar_url": url,
            "source": source, "checked_on": checked_on,
        })
    for destination, data in originals.items():
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
    CONFIG_PATH.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    (PROFILE / "discord-profiles.json").write_text(json.dumps(profiles, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"Saved {len(profiles)} verified public Discord profiles and original avatars. Run build_profile.py next.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checked-on", required=True, help="Date in your local timezone, YYYY-MM-DD")
    sync(parser.parse_args().checked_on)
