"""Unit tests for Slack slash command endpoint."""
import hmac
import hashlib
import time
import unittest
from unittest.mock import patch, MagicMock

from slack_app import (
    app,
    _verify_slack_signature,
    _is_timestamp_fresh,
    _parse_job_type,
    SLACK_TIMESTAMP_MAX_AGE,
)


def _make_signed_body(secret: str, body: str, timestamp: str) -> str:
    """Build X-Slack-Signature value for body and timestamp."""
    sig_basestring = f"v0:{timestamp}:{body}"
    sig = "v0=" + hmac.new(
        secret.encode(), sig_basestring.encode(), hashlib.sha256
    ).hexdigest()
    return sig


class TestParseJobType(unittest.TestCase):
    def test_empty_defaults_daily(self):
        self.assertEqual(_parse_job_type(""), "daily")
        self.assertEqual(_parse_job_type("   "), "daily")
        self.assertEqual(_parse_job_type(None), "daily")

    def test_daily(self):
        self.assertEqual(_parse_job_type("daily"), "daily")
        self.assertEqual(_parse_job_type("  daily  "), "daily")
        self.assertEqual(_parse_job_type("DAILY"), "daily")

    def test_monday(self):
        self.assertEqual(_parse_job_type("monday"), "monday")
        self.assertEqual(_parse_job_type("  monday  "), "monday")

    def test_friday(self):
        self.assertEqual(_parse_job_type("friday"), "friday")
        self.assertEqual(_parse_job_type("  friday  "), "friday")

    def test_unknown_defaults_daily(self):
        self.assertEqual(_parse_job_type("other"), "daily")
        self.assertEqual(_parse_job_type("weekly"), "daily")


class TestTimestampFresh(unittest.TestCase):
    def test_fresh(self):
        ts = str(int(time.time()))
        self.assertTrue(_is_timestamp_fresh(ts))

    def test_too_old(self):
        ts = str(int(time.time()) - SLACK_TIMESTAMP_MAX_AGE - 60)
        self.assertFalse(_is_timestamp_fresh(ts))

    def test_invalid(self):
        self.assertFalse(_is_timestamp_fresh(""))
        self.assertFalse(_is_timestamp_fresh("abc"))
        self.assertFalse(_is_timestamp_fresh(None))


class TestVerifySlackSignature(unittest.TestCase):
    def test_missing_secret_skips_verification(self):
        body = b"token=x&team_id=T&timestamp=123&text=daily"
        with patch.dict("os.environ", {"SLACK_SIGNING_SECRET": ""}, clear=False):
            # When SLACK_SIGNING_SECRET is not set (empty), verification is skipped (returns True)
            self.assertTrue(
                _verify_slack_signature(body, "123", "v0=anything")
            )

    def test_valid_signature(self):
        secret = "test_signing_secret"
        timestamp = "1234567890"
        body = b"token=x&team_id=T&timestamp=1234567890&text=daily"
        sig = _make_signed_body(secret, body.decode("utf-8"), timestamp)
        with patch.dict("os.environ", {"SLACK_SIGNING_SECRET": secret}):
            self.assertTrue(
                _verify_slack_signature(body, timestamp, sig)
            )

    def test_invalid_signature(self):
        body = b"token=x&timestamp=1234567890&text=daily"
        with patch.dict("os.environ", {"SLACK_SIGNING_SECRET": "secret"}):
            self.assertFalse(
                _verify_slack_signature(body, "1234567890", "v0=wronghex")
            )
            self.assertFalse(
                _verify_slack_signature(body, "1234567890", "")
            )
            self.assertFalse(
                _verify_slack_signature(body, "", "v0=something")
            )


class TestSlashCommandEndpoint(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def _post(
        self,
        body: str,
        signature: str = None,
        timestamp: str = None,
    ):
        if timestamp is None:
            timestamp = str(int(time.time()))
        if signature is None and "SLACK_SIGNING_SECRET" in __import__("os").environ:
            secret = __import__("os").environ["SLACK_SIGNING_SECRET"]
            signature = _make_signed_body(secret, body, timestamp)
        headers = {}
        if signature:
            headers["X-Slack-Signature"] = signature
        return self.client.post(
            "/slack/weekly-update",
            data=body,
            content_type="application/x-www-form-urlencoded",
            headers=headers,
        )

    def test_missing_signature_401(self):
        body = f"token=x&team_id=T&timestamp={int(time.time())}&text=daily"
        with patch.dict("os.environ", {"SLACK_SIGNING_SECRET": "secret"}):
            r = self.client.post(
                "/slack/weekly-update",
                data=body,
                content_type="application/x-www-form-urlencoded",
            )
        self.assertEqual(r.status_code, 401)

    def test_invalid_signature_401(self):
        ts = str(int(time.time()))
        body = f"token=x&team_id=T&timestamp={ts}&text=daily"
        with patch.dict("os.environ", {"SLACK_SIGNING_SECRET": "secret"}):
            r = self.client.post(
                "/slack/weekly-update",
                data=body,
                content_type="application/x-www-form-urlencoded",
                headers={"X-Slack-Signature": "v0=invalid"},
            )
        self.assertEqual(r.status_code, 401)

    def test_old_timestamp_401(self):
        secret = "test_secret"
        ts = str(int(time.time()) - SLACK_TIMESTAMP_MAX_AGE - 60)
        body = f"token=x&team_id=T&timestamp={ts}&text=daily&response_url=https://hooks.slack.com/foo"
        sig = _make_signed_body(secret, body, ts)
        with patch.dict("os.environ", {"SLACK_SIGNING_SECRET": secret}):
            r = self.client.post(
                "/slack/weekly-update",
                data=body,
                content_type="application/x-www-form-urlencoded",
                headers={"X-Slack-Signature": sig},
            )
        self.assertEqual(r.status_code, 401)

    def test_valid_request_dispatches_job_and_returns_200(self):
        secret = "test_secret"
        ts = str(int(time.time()))
        body = f"token=x&team_id=T&timestamp={ts}&text=daily&response_url=https://hooks.slack.com/foo"
        sig = _make_signed_body(secret, body, ts)
        with patch.dict("os.environ", {"SLACK_SIGNING_SECRET": secret}):
            with patch("scheduler.WeeklyUpdateScheduler", MagicMock()):
                with patch("slack_app.threading") as mock_threading:
                    mock_thread = MagicMock()
                    mock_threading.Thread.return_value = mock_thread
                    r = self.client.post(
                        "/slack/weekly-update",
                        data=body,
                        content_type="application/x-www-form-urlencoded",
                        headers={"X-Slack-Signature": sig},
                    )
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertIn("Running daily update", data["text"])
        mock_thread.start.assert_called_once()

    def test_text_monday_response_contains_monday(self):
        secret = "test_secret"
        ts = str(int(time.time()))
        body = f"token=x&team_id=T&timestamp={ts}&text=monday&response_url=https://hooks.slack.com/foo"
        sig = _make_signed_body(secret, body, ts)
        with patch.dict("os.environ", {"SLACK_SIGNING_SECRET": secret}):
            with patch("slack_app.threading") as mock_threading:
                mock_thread = MagicMock()
                mock_threading.Thread.return_value = mock_thread
                r = self.client.post(
                    "/slack/weekly-update",
                    data=body,
                    content_type="application/x-www-form-urlencoded",
                    headers={"X-Slack-Signature": sig},
                )
        self.assertEqual(r.status_code, 200)
        self.assertIn("monday", r.get_json()["text"].lower())

    def test_empty_body_400(self):
        with patch.dict("os.environ", {"SLACK_SIGNING_SECRET": "secret"}):
            r = self.client.post(
                "/slack/weekly-update",
                data="",
                content_type="application/x-www-form-urlencoded",
            )
        self.assertEqual(r.status_code, 400)


if __name__ == "__main__":
    unittest.main()
