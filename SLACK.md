# Slack app setup and testing

This guide covers creating the slash command in the Slack API, installing the app, and testing with ngrok or curl. To host the app so your whole team can use `/weekly-update` without running anything locally, see **Deploy to Render** in the main [README](README.md).

**Important:** Slack requires a non-empty **Request URL** before you can save the slash command. For local testing you must start the app and ngrok first (see below), then use the ngrok URL when creating the command.

## Get a Request URL first (local testing)

1. Set your signing secret and start the app:
   ```bash
   export SLACK_SIGNING_SECRET="your-signing-secret-from-basic-information"
   python slack_app.py
   ```
2. In a **second terminal**, start ngrok to expose port 5000:
   ```bash
   ngrok http 5000
   ```
3. Copy the HTTPS URL ngrok shows (e.g. `https://abc123.ngrok-free.app`). Your Request URL will be: `https://abc123.ngrok-free.app/slack/weekly-update`. Keep the app and ngrok running while you complete the next section.

## Create the slash command

1. Go to [api.slack.com/apps](https://api.slack.com/apps) and open your app (or create one).
2. Under **Features**, click **Slash Commands** → **Create New Command**.
3. Set:
   - **Command:** `/weekly-update` (or the name you want).
   - **Request URL:** Your app endpoint. For local testing use the ngrok URL from above, e.g. `https://YOUR_NGROK_HOST/slack/weekly-update`. For production use your server URL, e.g. `https://your-server.com/slack/weekly-update`. This field cannot be empty.
   - **Short Description:** e.g. `Trigger weekly update (daily / monday / friday)`.
   - **Usage Hint (optional):** `[daily|monday|friday]`
4. Save.

## Install the app to your workspace

1. In the app settings, go to **Install App** (or **OAuth & Permissions**).
2. Click **Install to Workspace** and authorize the app for the workspace you use.
3. Copy the **Signing Secret** from **Basic Information** and set it as `SLACK_SIGNING_SECRET` where you run `slack_app.py`.

## Environment variable

Set the signing secret before starting the app:

```bash
export SLACK_SIGNING_SECRET="your-signing-secret-from-basic-information"
python slack_app.py
```

## Manual testing

After creating the slash command with your Request URL, go to Slack and run `/weekly-update` or `/weekly-update daily`. You should get an immediate reply and (when the job finishes) a completion message. Keep `slack_app.py` and ngrok running while testing.

### With curl (signature verification)

To test the endpoint with a valid signature (replace `YOUR_SIGNING_SECRET` and ensure the body and timestamp match the signature):

```bash
# Example: body and timestamp used to compute signature
TIMESTAMP=$(date +%s)
BODY="token=x&team_id=T&timestamp=${TIMESTAMP}&text=daily&response_url=https://hooks.slack.com/foo"
SIG="v0=$(echo -n "v0:${TIMESTAMP}:${BODY}" | openssl dgst -sha256 -hmac "YOUR_SIGNING_SECRET" | awk '{print $2}')"

curl -X POST http://localhost:5000/slack/weekly-update \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "X-Slack-Signature: $SIG" \
  -d "$BODY"
```

You should get a 200 JSON response with text like "Running daily update…".

## Unit tests

Run the Slack slash command tests (requires dependencies from `requirements.txt`):

```bash
python -m unittest test_slack_slash_command -v
```

Tests cover signature verification (valid → 200, invalid/missing → 401), replay protection (old timestamp → 401), job type parsing (`text` → daily/monday/friday), and response content.
