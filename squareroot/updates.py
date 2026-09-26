"""On-demand update check against GitHub Releases.

Design (see docs/Updates.md):
* runs ONLY when the user clicks "Help -> Check for updates" -- no background
  traffic, no telemetry;
* writes nothing to disk and never replaces the running binary: it only
  reports the newest version and the release page URL, the user downloads
  the new portable file and deletes the old one;
* standard library only (urllib + json), 5 s timeout, every failure becomes
  an UpdateCheckError so the GUI can show a localized message.
"""

import json
import re
import urllib.error
import urllib.request
from dataclasses import dataclass

from . import __version__

# Override at build time if the repository is forked/renamed.
GITHUB_REPO = "imredtea/SquareRoot"
LATEST_RELEASE_API = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
RELEASES_PAGE = f"https://github.com/{GITHUB_REPO}/releases/latest"
TIMEOUT_SECONDS = 5

_VERSION_RE = re.compile(r"^v?(\d+(?:\.\d+)*)")


class UpdateCheckError(Exception):
    """Network failure, no releases yet, or an unexpected server response."""


@dataclass(frozen=True)
class UpdateInfo:
    current: str
    latest: str
    url: str

    @property
    def is_newer(self):
        return parse_version(self.latest) > parse_version(self.current)


def parse_version(text):
    """'v1.2.3' / '1.2' / '1.2.3-rc1' -> (1, 2, 3) / (1, 2, 0) / (1, 2, 3)."""
    match = _VERSION_RE.match(str(text).strip())
    if not match:
        raise UpdateCheckError(f"not a version: {text!r}")
    parts = [int(p) for p in match.group(1).split(".")]
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts)


def check_for_update(current=__version__, opener=urllib.request.urlopen):
    request = urllib.request.Request(
        LATEST_RELEASE_API,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": f"SquareRoot/{current}",
        },
    )
    try:
        with opener(request, timeout=TIMEOUT_SECONDS) as response:
            data = json.loads(response.read().decode("utf-8"))
        tag = data["tag_name"]
        url = data.get("html_url") or RELEASES_PAGE
    except (urllib.error.URLError, OSError, ValueError, KeyError, TypeError) as e:
        raise UpdateCheckError(str(e)) from None
    parse_version(tag)  # validate
    return UpdateInfo(current=current, latest=tag.lstrip("v"), url=url)
