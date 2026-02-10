"""Flask app for Slack slash command: trigger weekly updates from Slack."""
import hmac
import hashlib
import json
import logging
import os
import threading
import time
from urllib.parse import parse_qs

import requests
from flask import Flask, request, jsonify

DEBUG_LOG_PATH = os.path.join(os.path.dirname(__file__), ".cursor", "debug.log")

def _debug_log(message: str, data: dict, hypothesis_id: str = ""):
    try:
        payload = {"message": message, "data": data, "timestamp": int(time.time() * 1000)}
        if hypothesis_id:
            payload["hypothesisId"] = hypothesis_id
        with open(DEBUG_LOG_PATH, "a") as f:
            f.write(json.dumps(payload) + "\n")
    except Exception:
        pass

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
        logger.info(
            "Signature verification failed: missing or invalid X-Slack-Signature (has_header=%s, starts_v0=%s)",
            bool(signature_header),
            signature_header.startswith("v0=") if signature_header else False,
        )
        return False
    if not timestamp:
        logger.info("Signature verification failed: missing timestamp in body")
        return False
    body_str = body_bytes.decode("utf-8")
    sig_basestring = f"v0:{timestamp}:{body_str}"
    computed = "v0=" + hmac.new(
        secret.encode(), sig_basestring.encode(), hashlib.sha256
    ).hexdigest()
    ok = hmac.compare_digest(computed, signature_header)
    if not ok:
        logger.info(
            "Signature verification failed: computed != received (body_len=%d, timestamp=%s)",
            len(body_bytes),
            timestamp,
        )
    return ok


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
    # #region agent log
    _debug_log("slack_weekly_update entry", {}, "A")
    # #endregion
    try:
        # Need raw body for signature verification (Slack sends form-urlencoded).
        # parse_form_data=False ensures we get the exact bytes Slack sent (no re-encoding).
        body_bytes = request.get_data(parse_form_data=False)
        if not body_bytes:
            logger.info("Slack request rejected: empty body")
            _debug_log("empty body return 400", {}, "B")
            return jsonify({"text": "Empty body"}), 400

        sig_header = request.headers.get("X-Slack-Signature")
        data = parse_qs(body_bytes.decode("utf-8"))
        # Slack sends timestamp in X-Slack-Request-Timestamp header (not in body) for signature verification
        timestamp = (request.headers.get("X-Slack-Request-Timestamp") or "").strip()
        if not timestamp:
            timestamp = (data.get("timestamp") or [None])[0]
        timestamp = (timestamp or "").strip() if timestamp else ""
        body_hash = hashlib.sha256(body_bytes).hexdigest()[:12]
        logger.info(
            "Slack request received: body_len=%d, body_sha256_prefix=%s, has_sig=%s, has_timestamp=%s, timestamp=%s",
            len(body_bytes),
            body_hash,
            bool(sig_header),
            bool(timestamp),
            timestamp if timestamp else "(none)",
        )
        sig_ok = _verify_slack_signature(body_bytes, timestamp, sig_header or "")
        # #region agent log
        _debug_log("after signature verify", {"sig_ok": sig_ok, "has_timestamp": bool(timestamp)}, "B")
        # #endregion
        if not sig_ok:
            logger.info("Slack request rejected: invalid signature")
            return jsonify({"text": "Invalid signature"}), 401
        fresh = timestamp and _is_timestamp_fresh(timestamp)
        if not fresh:
            logger.info(
                "Slack request rejected: timestamp too old (timestamp=%s, now=%s)",
                timestamp,
                int(time.time()),
            )
        # #region agent log
        _debug_log("after timestamp check", {"fresh": fresh}, "B")
        # #endregion
        if not fresh:
            return jsonify({"text": "Request too old"}), 401

        logger.info("Slack request accepted: signature valid, timestamp fresh")
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
        # #region agent log
        _debug_log("returning 200", {"job_type": job_type, "response_type": reply.get("response_type")}, "C")
        # #endregion
        return jsonify(reply), 200
    except Exception as e:
        # #region agent log
        _debug_log("handler exception", {"error": str(e), "type": type(e).__name__}, "D")
        # #endregion
        logger.exception("Slack slash command handler error")
        return jsonify({"text": f"Error: {str(e)}"}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    secret = os.getenv("SLACK_SIGNING_SECRET") or ""
    logger.info(
        "SLACK_SIGNING_SECRET present: %s, first_6_chars: %s",
        bool(secret),
        secret[:6] if secret else "(none)",
    )
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
