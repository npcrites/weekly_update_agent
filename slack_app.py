"""Flask app for Slack slash command: trigger weekly updates from Slack."""
import hmac
import hashlib
import logging
import os
import threading
import time
from urllib.parse import parse_qs

import requests
from flask import Flask, request, jsonify

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Max age of request timestamp (seconds) to avoid replay
SLACK_TIMESTAMP_MAX_AGE = 60 * 5


def _verify_slack_signature(
    body_bytes: bytes, timestamp: str, signature_header: str
) -> bool:
    """Verify X-Slack-Signature: v0=<hex> using SLACK_SIGNING_SECRET."""
    secret = os.getenv("SLACK_SIGNING_SECRET")
    if not secret:
        logger.warning("SLACK_SIGNING_SECRET not set; skipping verification")
        return True
    if not signature_header or not signature_header.startswith("v0="):
        return False
    if not timestamp:
        return False
    body_str = body_bytes.decode("utf-8")
    sig_basestring = f"v0:{timestamp}:{body_str}"
    computed = "v0=" + hmac.new(
        secret.encode(), sig_basestring.encode(), hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(computed, signature_header)


def _is_timestamp_fresh(timestamp_str: str) -> bool:
    """Return True if timestamp is within SLACK_TIMESTAMP_MAX_AGE."""
    try:
        ts = int(timestamp_str)
    except (ValueError, TypeError):
        return False
    return abs(time.time() - ts) <= SLACK_TIMESTAMP_MAX_AGE


def _parse_job_type(text: str) -> str:
    """Map slash command text to scheduler job type: monday, friday, or daily."""
    t = (text or "").strip().lower()
    if t == "monday":
        return "monday"
    if t == "friday":
        return "friday"
    return "daily"


def _run_job_and_notify(job_type: str, response_url: str) -> None:
    """Run the scheduler job, then POST success/failure to response_url."""
    try:
        from scheduler import WeeklyUpdateScheduler

        scheduler = WeeklyUpdateScheduler()
        scheduler.run_now(job_type)
        payload = {"text": f"Weekly update job `{job_type}` completed successfully."}
    except Exception as e:
        logger.exception("Slack-triggered job failed")
        payload = {
            "text": f"Weekly update job `{job_type}` failed: {str(e)}",
            "response_type": "ephemeral",
        }
    try:
        requests.post(response_url, json=payload, timeout=10)
    except Exception as e:
        logger.warning("Failed to post to response_url: %s", e)


@app.route("/slack/weekly-update", methods=["POST"])
def slack_weekly_update():
    """Handle Slack slash command: run weekly update job and respond quickly."""
    # Need raw body for signature verification (Slack sends form-urlencoded)
    body_bytes = request.get_data()
    if not body_bytes:
        return jsonify({"text": "Empty body"}), 400

    sig_header = request.headers.get("X-Slack-Signature")
    data = parse_qs(body_bytes.decode("utf-8"))
    timestamp = (data.get("timestamp") or [None])[0]
    if not _verify_slack_signature(body_bytes, timestamp or "", sig_header or ""):
        return jsonify({"text": "Invalid signature"}), 401
    if not timestamp or not _is_timestamp_fresh(timestamp):
        return jsonify({"text": "Request too old"}), 401

    text = (data.get("text") or [""])[0]
    response_url = (data.get("response_url") or [""])[0]
    job_type = _parse_job_type(text)

    # Respond within 3 seconds
    reply = {
        "response_type": "ephemeral",
        "text": f"Running {job_type} update… I'll post here when it's done.",
    }
    if not response_url:
        reply["text"] = f"Running {job_type} update… (no response_url; check logs for completion)"

    # Run job in background and optionally post to response_url when done
    def run():
        if response_url:
            _run_job_and_notify(job_type, response_url)
        else:
            try:
                from scheduler import WeeklyUpdateScheduler

                WeeklyUpdateScheduler().run_now(job_type)
            except Exception as e:
                logger.exception("Slack-triggered job failed: %s", e)

    threading.Thread(target=run, daemon=True).start()
    return jsonify(reply), 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    try:
        import waitress

        for attempt in range(10):
            try:
                logger.info("Starting Slack app on port %s", port)
                waitress.serve(app, host="0.0.0.0", port=port)
                break
            except OSError as e:
                if e.errno == 48 and attempt < 9:  # Address already in use
                    port += 1
                    continue
                raise
    except ImportError:
        app.run(host="0.0.0.0", port=port)
