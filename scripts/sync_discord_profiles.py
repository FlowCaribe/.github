"""Synchronize public Discord names, usernames, avatars and banners.

Fetches all profiles before writing. Roles and editorial names stay under
the team's control. Unchanged snapshots produce no file changes or bot commits.
"""
from __future__ import annotations

import argparse
from datetime import date, datetime, timedelta, timezone
import json
from pathlib import Path
import re
import struct
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "profile"
API = "https://www.vibebot.gg/api/tools/avatar-lookup?id="
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def local_today() -> str:
    return datetime.now(timezone(timedelta(hours=-6))).date().isoformat()


def download(url: str, limit: int) -> bytes:
    request = Request(url, headers={"User-Agent": "FlowCaribe-Profile/1.0"})
    with urlopen(request, timeout=30) as response:
        if urlsplit(url).netloc == "cdn.discordapp.com" and urlsplit(response.geturl()).netloc != "cdn.discordapp.com":
            raise ValueError("Discord images must stay on the official CDN")
        data = response.read(limit + 1)
    if len(data) > limit:
        raise ValueError("Response exceeds the allowed size")
    return data


def check_png(data: bytes) -> None:
    if len(data) < 45 or not data.startswith(PNG_SIGNATURE) or data[12:16] != b"IHDR":
        raise ValueError("Discord image is not a PNG")
    width, height = struct.unpack(">II", data[16:24])
    if not 1 <= width <= 4096 or not 1 <= height <= 4096:
        raise ValueError("Unexpected Discord image dimensions")
    if data[-12:] != b"\x00\x00\x00\x00IEND\xaeB\x60\x82":
        raise ValueError("Discord PNG is incomplete")


def team_path(profile: Path, value: str) -> Path:
    destination = (profile / "assets" / value).resolve()
    if not destination.is_relative_to((profile / "assets" / "team").resolve()) or destination.suffix != ".png":
        raise ValueError("Discord images must be PNGs inside assets/team")
    return destination


def public_label(value: object, kind: str) -> str:
    if not isinstance(value, str) or not 1 <= len(value) <= 32 or any(ord(character) < 32 for character in value):
        raise ValueError(f"Invalid public Discord {kind}")
    return value


def lookup(person: dict) -> tuple[dict, str, bytes, str | None, bytes | None]:
    user_id = person["discord_id"]
    if not isinstance(user_id, str) or not re.fullmatch(r"\d{17,20}", user_id):
        raise ValueError("Invalid Discord user ID")
    payload = json.loads(download(API + user_id, 100_000))
    user = payload["user"]
    if user.get("id") != user_id:
        raise ValueError("The lookup returned a different user")
    public_label(user.get("username"), "username")
    if user.get("global_name") is not None:
        public_label(user["global_name"], "display name")
    avatar_url = ((payload.get("avatar") or {}).get("png") or {}).get("256") or payload.get("defaultAvatar")
    parsed = urlsplit(avatar_url or "")
    if parsed.scheme != "https" or parsed.netloc != "cdn.discordapp.com":
        raise ValueError("Avatar must originate from Discord's official CDN")
    if not parsed.path.startswith((f"/avatars/{user_id}/", "/embed/avatars/")):
        raise ValueError("Unexpected Discord avatar path")
    avatar = download(avatar_url, 2_000_000)
    check_png(avatar)
    banner_hash = user.get("banner")
    banner_url = None
    banner = None
    if banner_hash:
        if not isinstance(banner_hash, str) or not re.fullmatch(r"(?:a_)?[a-f0-9]{32}", banner_hash):
            raise ValueError("Invalid Discord banner hash")
        banner_url = f"https://cdn.discordapp.com/banners/{user_id}/{banner_hash}.png?size=1024"
        banner = download(banner_url, 2_000_000)
        check_png(banner)
    return user, avatar_url, avatar, banner_url, banner


def write_if_changed(path: Path, data: bytes) -> bool:
    if path.exists() and path.read_bytes() == data:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return True


def sync(checked_on: str, profile: Path = PROFILE) -> bool:
    date.fromisoformat(checked_on)
    config_path = profile / "profile.json"
    state_path = profile / "discord-profiles.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    previous = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else []
    previous_by_id = {entry["id"]: entry for entry in previous}
    originals = {}
    removed_banners = []
    profiles = []
    for person in config["developers"]:
        if not re.fullmatch(r"[a-z][a-z0-9-]{0,63}", person["slug"]):
            raise ValueError("Invalid image slug")
        user, avatar_url, avatar, banner_url, banner = lookup(person)
        avatar_destination = team_path(profile, person["avatar"])
        originals[avatar_destination] = avatar
        banner_path = f'team/{person["slug"]}-banner.png' if banner is not None else None
        if banner_path:
            originals[team_path(profile, banner_path)] = banner
        elif person.get("discord_banner"):
            removed_banners.append(team_path(profile, person["discord_banner"]))
        person["discord_username"] = user["username"]
        person["discord_display_name"] = user.get("global_name") or user["username"]
        person["discord_banner"] = banner_path
        entry = {
            "name": person["name"], "id": person["discord_id"], "username": user["username"],
            "global_name": user.get("global_name"), "avatar_url": avatar_url, "banner_url": banner_url,
            "source": API + person["discord_id"], "checked_on": checked_on,
        }
        old_entry = previous_by_id.get(person["discord_id"], {})
        same_identity = {k: v for k, v in entry.items() if k != "checked_on"} == {k: v for k, v in old_entry.items() if k != "checked_on"}
        media = {avatar_destination: avatar}
        if banner_path:
            media[team_path(profile, banner_path)] = banner
        if same_identity and all(path.exists() and path.read_bytes() == data for path, data in media.items()):
            entry["checked_on"] = old_entry["checked_on"]
        profiles.append(entry)
    # No file is touched until every response and destination has been validated.
    changed = False
    for destination, data in originals.items():
        changed = write_if_changed(destination, data) or changed
    for destination in removed_banners:
        if destination.exists():
            destination.unlink()
            changed = True
    encoded = lambda value: (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    changed = write_if_changed(config_path, encoded(config)) or changed
    changed = write_if_changed(state_path, encoded(profiles)) or changed
    print(f"Discord profiles {'updated' if changed else 'unchanged'}: {len(profiles)} verified identities. Roles preserved.")
    return changed


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checked-on", default=local_today(), help="Snapshot date, YYYY-MM-DD (default: Costa Rica today)")
    sync(parser.parse_args().checked_on)
