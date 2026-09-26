"""Update check: all network access mocked (no real HTTP in tests)."""

import io
import json
import unittest
import urllib.error

from squareroot import updates
from squareroot.ui.logic import describe_update


class _Response(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def _opener(payload):
    def opener(request, timeout):
        assert timeout == updates.TIMEOUT_SECONDS
        assert request.full_url == updates.LATEST_RELEASE_API
        return _Response(json.dumps(payload).encode())
    return opener


def _failing(exc):
    def opener(request, timeout):
        raise exc
    return opener


class ParseVersion(unittest.TestCase):
    def test_forms(self):
        self.assertEqual(updates.parse_version("v1.2.3"), (1, 2, 3))
        self.assertEqual(updates.parse_version("1.2"), (1, 2, 0))
        self.assertEqual(updates.parse_version("2.0.1-rc1"), (2, 0, 1))
        self.assertGreater(updates.parse_version("0.10.0"), updates.parse_version("0.9.9"))

    def test_garbage(self):
        with self.assertRaises(updates.UpdateCheckError):
            updates.parse_version("latest")


class CheckForUpdate(unittest.TestCase):
    def test_newer_release(self):
        info = updates.check_for_update(
            "0.1.0", _opener({"tag_name": "v0.2.0", "html_url": "https://example/r"})
        )
        self.assertEqual((info.latest, info.url, info.is_newer), ("0.2.0", "https://example/r", True))

    def test_same_release_and_default_url(self):
        info = updates.check_for_update("0.1.0", _opener({"tag_name": "v0.1.0"}))
        self.assertFalse(info.is_newer)
        self.assertEqual(info.url, updates.RELEASES_PAGE)

    def test_failures_become_update_check_error(self):
        for opener in (
            _failing(urllib.error.URLError("offline")),
            _failing(TimeoutError()),
            _opener({"message": "Not Found"}),
            _opener({"tag_name": "nightly"}),
        ):
            with self.assertRaises(updates.UpdateCheckError):
                updates.check_for_update("0.1.0", opener)


class DescribeUpdate(unittest.TestCase):
    def test_available_all_languages(self):
        info = updates.UpdateInfo("0.1.0", "0.2.0", "https://example/r")
        for lang in ("ru", "en", "es", "zh", "ja"):
            msg = describe_update(lambda: info, lang)
            self.assertEqual(msg.kind, "available")
            self.assertIn("0.2.0", msg.message)
            self.assertEqual(msg.url, "https://example/r")

    def test_latest(self):
        msg = describe_update(lambda: updates.UpdateInfo("0.1.0", "0.1.0", "u"), "en")
        self.assertEqual((msg.kind, msg.url), ("latest", ""))

    def test_error_never_raises(self):
        def boom():
            raise updates.UpdateCheckError("offline")
        msg = describe_update(boom, "ru")
        self.assertEqual(msg.kind, "error")
        self.assertTrue(msg.message)


if __name__ == "__main__":
    unittest.main()
