#!/usr/bin/env python3
"""Validate the profile's local references and self-contained graphics offline."""

from __future__ import annotations

import base64
import binascii
from html.parser import HTMLParser
import math
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
MAX_SVG_BYTES = 1024 * 1024
ERRORS: list[str] = []
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
JPEG_SIGNATURE = b"\xff\xd8\xff"


def error(path: Path, message: str) -> None:
    ERRORS.append(f"{path.relative_to(ROOT).as_posix()}: {message}")


def check_reference(document: Path, target: str, *, image: bool = False) -> None:
    """Resolve local files, including raw GitHub URLs targeting this profile."""
    target = target.strip()
    if not target or target.startswith("#"):
        error(document, f"empty or placeholder destination: {target!r}")
        return
    parsed = urlsplit(target)
    if parsed.scheme or parsed.netloc:
        if parsed.scheme != "https" or not parsed.netloc:
            error(document, f"public URLs must use HTTPS: {target}")
            return
        if not image:
            return
        # /OWNER/REPOSITORY/REF/profile/... maps to this checkout's profile/.
        parts = unquote(parsed.path).strip("/").split("/")
        if parsed.hostname == "raw.githubusercontent.com" and len(parts) >= 5 and parts[3] == "profile":
            local = ROOT.joinpath(*parts[3:])
        else:
            error(document, f"image must be a local asset or a raw GitHub profile asset: {target}")
            return
    else:
        if "\\" in parsed.path:
            error(document, f"use forward slashes in references: {target}")
            return
        decoded = unquote(parsed.path)
        local = ROOT / decoded.lstrip("/") if decoded.startswith("/") else document.parent / decoded
    local = local.resolve()
    if not local.is_relative_to(ROOT):
        error(document, f"reference escapes the repository: {target}")
    elif not local.is_file():
        error(document, f"referenced file does not exist: {target}")


class ReadmeParser(HTMLParser):
    def __init__(self, document: Path) -> None:
        super().__init__(convert_charrefs=True)
        self.document = document
        self.pictures: list[dict[str, int]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        line = self.getpos()[0]
        if tag == "picture":
            self.pictures.append({"images": 0, "sources": 0, "line": line})
        if tag == "img":
            if "alt" not in values:
                error(self.document, f"line {line}: <img> requires an alt attribute")
            check_reference(self.document, values.get("src") or "", image=True)
            if self.pictures:
                self.pictures[-1]["images"] += 1
        if tag in {"source", "img"} and "srcset" in values:
            candidates = (values["srcset"] or "").split(",")
            for candidate in candidates:
                tokens = candidate.strip().split()
                check_reference(self.document, tokens[0] if tokens else "", image=True)
            if tag == "source" and self.pictures:
                self.pictures[-1]["sources"] += 1
        elif tag == "source":
            error(self.document, f"line {line}: <source> requires srcset")
        if tag == "a":
            check_reference(self.document, values.get("href") or "")

    def handle_endtag(self, tag: str) -> None:
        if tag == "picture" and self.pictures:
            picture = self.pictures.pop()
            if picture["images"] != 1 or picture["sources"] < 1:
                error(self.document, f"line {picture['line']}: <picture> requires sources and one fallback <img>")

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)


def check_readme(document: Path) -> None:
    if not document.is_file():
        error(document, "required README is missing")
        return
    text = document.read_text(encoding="utf-8")
    # Code examples are documentation, not rendered links or images.
    text = re.sub(r"^\s*(`{3,}|~{3,})[^\n]*\n.*?^\s*\1\s*$", "", text, flags=re.M | re.S)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    parser = ReadmeParser(document)
    parser.feed(text)
    parser.close()
    if parser.pictures:
        error(document, "unclosed <picture> element")
    # Inline Markdown links and images; optional link titles are ignored.
    for match in re.finditer(r"(!?)\[([^\]\n]*)\]\(\s*(?:<([^>]+)>|([^\s)]+))(?:\s+['\"][^\n]*?['\"])?\s*\)", text):
        check_reference(document, match[3] or match[4], image=bool(match[1]))
    definitions = {
        match[1].strip().casefold(): match[2] or match[3]
        for match in re.finditer(r"^\s{0,3}\[([^\]]+)\]:\s*(?:<([^>]+)>|(\S+))", text, re.M)
    }
    for match in re.finditer(r"(!?)\[([^\]\n]+)\]\[([^\]\n]*)\]", text):
        label = (match[3] or match[2]).strip().casefold()
        if label not in definitions:
            error(document, f"undefined Markdown link reference: {label}")
        else:
            check_reference(document, definitions[label], image=bool(match[1]))
    for destination in definitions.values():
        check_reference(document, destination)


def check_raster(path: Path, data: bytes, mime: str) -> None:
    if mime == "image/png":
        if not data.startswith(PNG_SIGNATURE) or data[12:16] != b"IHDR":
            error(path, "PNG data does not match its extension or declared MIME type")
    elif mime == "image/jpeg":
        if not data.startswith(JPEG_SIGNATURE) or not data.endswith(b"\xff\xd9"):
            error(path, "JPEG data does not match its extension or declared MIME type")


def check_svg(path: Path) -> None:
    data = path.read_bytes()
    if len(data) >= MAX_SVG_BYTES:
        error(path, f"SVG must be smaller than 1 MiB (found {len(data):,} bytes)")
    if re.search(br"<!\s*(?:DOCTYPE|ENTITY)\b", data, re.I):
        error(path, "SVG must not declare document types or entities")
        return
    try:
        root = ET.fromstring(data)
    except ET.ParseError as exc:
        error(path, f"invalid SVG XML: {exc}")
        return
    if root.tag != "{http://www.w3.org/2000/svg}svg":
        error(path, "root must be an SVG element with the SVG namespace")
    try:
        viewbox = [float(value) for value in re.split(r"[\s,]+", root.attrib.get("viewBox", "").strip())]
        if len(viewbox) != 4 or not all(math.isfinite(value) for value in viewbox) or min(viewbox[2:]) <= 0:
            raise ValueError
    except ValueError:
        error(path, "viewBox must contain four finite numbers with positive width and height")
    for required in ("title", "desc"):
        child = root.find(f"{{http://www.w3.org/2000/svg}}{required}")
        if child is None or not "".join(child.itertext()).strip():
            error(path, f"SVG requires a nonempty root <{required}>")
    for element in root.iter():
        tag = element.tag.rsplit("}", 1)[-1]
        if tag.lower() in {"script", "foreignobject"}:
            error(path, f"unsupported SVG element: {tag}")
        for attribute, value in element.attrib.items():
            attribute = attribute.rsplit("}", 1)[-1]
            if attribute.lower().startswith("on"):
                error(path, f"event handlers are prohibited: {attribute}")
            if attribute == "href":
                if value.startswith("#"):
                    continue
                match = re.fullmatch(r"data:(image/(?:png|jpeg));base64,([A-Za-z0-9+/=\s]+)", value)
                if tag != "image" or not match:
                    error(path, f"SVG references must be internal or embedded PNG/JPEG images: {value[:80]}")
                else:
                    try:
                        raster = base64.b64decode(re.sub(r"\s+", "", match[2]), validate=True)
                        check_raster(path, raster, match[1])
                    except (ValueError, binascii.Error):
                        error(path, "embedded image has invalid base64 data")
            if re.search(r"(?:https?:|file:|javascript:|//)", value, re.I) and not value.startswith("data:image/"):
                error(path, f"external or executable SVG attribute: {attribute}")
            for reference in re.findall(r"url\(\s*['\"]?([^)'\"\s]+)", value, re.I):
                if not reference.startswith("#"):
                    error(path, f"SVG url() references must be internal: {reference[:80]}")
        if tag == "style":
            css = "".join(element.itertext())
            if re.search(r"@import|@font-face|https?:|//", css, re.I):
                error(path, "SVG CSS must not depend on external URLs or fonts")
            for reference in re.findall(r"url\(\s*['\"]?([^)'\"\s]+)", css, re.I):
                if not reference.startswith("#"):
                    error(path, f"SVG CSS url() references must be internal: {reference[:80]}")


def main() -> int:
    for readme in (ROOT / "README.md", ROOT / "profile" / "README.md"):
        check_readme(readme)
    graphics = sorted((ROOT / "profile").rglob("*"))
    svg_count = 0
    raster_count = 0
    for path in graphics:
        if not path.is_file():
            continue
        suffix = path.suffix.lower()
        if suffix == ".svg":
            check_svg(path)
            svg_count += 1
        elif suffix in {".png", ".jpg", ".jpeg"}:
            check_raster(path, path.read_bytes(), "image/png" if suffix == ".png" else "image/jpeg")
            raster_count += 1
    if svg_count == 0:
        error(ROOT / "profile", "no SVG assets found")
    if ERRORS:
        print("Profile validation failed:", file=sys.stderr)
        for message in ERRORS:
            print(f"  - {message}", file=sys.stderr)
        return 1
    print(f"Profile validation passed: 2 READMEs, {svg_count} SVGs, {raster_count} raster assets.")
    print("Offline check: file references, accessibility metadata, SVG safety, and raster signatures.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
