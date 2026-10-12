"""The README's links and images point at files and headings that exist."""
import re

from pyramid import REPO_ROOT


def slug(heading: str) -> str:
    """GitHub's anchor for a heading: lower case, punctuation dropped, spaces to hyphens."""
    return re.sub(r"[^a-z0-9 -]", "", heading.lower()).replace(" ", "-")


def test_every_relative_link_and_anchor_in_the_readme_resolves():
    text = (REPO_ROOT / "README.md").read_text()
    anchors = {slug(h) for h in re.findall(r"^#{1,6} (.+)$", text, re.M)}
    for target in re.findall(r"\]\(([^)\s]+)\)", text):
        if target.startswith(("http://", "https://")):
            continue
        path, _, anchor = target.partition("#")
        assert not path or (REPO_ROOT / path).exists(), target
        assert not anchor or anchor in anchors, target
