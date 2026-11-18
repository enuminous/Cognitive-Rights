"""Verify archived source, generated transcription and relative Markdown links."""

import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = ROOT / "charter/UDCR-2025-02-01.original.html"
READABLE = ROOT / "charter/UDCR-2025-02-01.md"
# Pinned Git blob observed in the author's source repository before this build.
SOURCE_BLOB = "c0d44124f13bcea570fc35955ed40310153e838a"


class CharterParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.depth = 0
        self.active = None
        self.text = []
        self.blocks = []

    def handle_starttag(self, tag, attrs):
        if tag == "section":
            if self.depth:
                self.depth += 1
            elif dict(attrs).get("data-field") == "body":
                self.depth = 1
        if self.depth and tag in ("p", "h3", "h4"):
            self.active, self.text = tag, []
        if self.active and tag == "br":
            self.text.append(" ")

    def handle_endtag(self, tag):
        if self.active == tag:
            prefix = "## " if tag == "h3" else "### " if tag == "h4" else ""
            self.blocks.append(prefix + " ".join("".join(self.text).split()))
            self.active = None
        if tag == "section" and self.depth:
            self.depth -= 1

    def handle_data(self, data):
        if self.active:
            self.text.append(data)


def transcription(data):
    parser = CharterParser()
    parser.feed(data.decode("utf-8"))
    if len(parser.blocks) < 25:
        raise ValueError("Unexpected source structure")
    blocks = parser.blocks
    blocks[0] = "# Universal Declaration of Cognitive Rights"
    return ("\n\n".join(blocks) + "\n\n---\n\n"
            "Historical text by Matthew Chenoweth Wright, February 1, 2025. "
            "Formatting-only transcription; see [provenance](PROVENANCE.md) and "
            "[claims boundaries](../docs/CLAIMS_BOUNDARY.md).\n")


def main():
    data = ORIGINAL.read_bytes()
    git_blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    if git_blob != SOURCE_BLOB:
        raise ValueError("Original source differs from pinned upstream Git blob")
    manifest = json.loads((ROOT / "charter/source-manifest.json").read_text())
    if manifest["sha256"] != hashlib.sha256(data).hexdigest() or manifest["git_blob_sha1"] != git_blob:
        raise ValueError("Source manifest mismatch")
    rendered = transcription(data)
    if "--render" in sys.argv:
        READABLE.write_text(rendered, encoding="utf-8")
    if READABLE.read_text(encoding="utf-8") != rendered:
        raise ValueError("Readable charter differs from deterministic transcription")
    for path in ROOT.rglob("*.md"):
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", path.read_text()):
            if "://" in target or target.startswith(("#", "mailto:")):
                continue
            if not (path.parent / target.split("#")[0]).exists():
                raise ValueError(f"Broken link in {path.relative_to(ROOT)}: {target}")
    print("PASS: original source, manifest, readable charter and local Markdown links")


if __name__ == "__main__":
    main()
