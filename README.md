# Weekly Update Automation Agent

Automated system that generates and maintains weekly update documents in Confluence, pulling insights from Jira, Glean, and Pendo.

## Features

- **Monday File Creation**: Automatically creates a new weekly update document every Monday
- **Daily Updates**: Updates the current weekly file every day at 8pm with new content
- **Friday Compile**: On Fridays at 8:30pm, compiles the week’s content into one cohesive document (no dupes)
- **Multi-Source Integration**: Pulls data from Jira, Glean, Pendo, and Granola
- **Tone Matching**: Learns from past documents to match your writing style
- **SVP Focus**: Highlights strategic items relevant to SVP of Product
- **Duplicate Prevention**: Tracks added content to avoid repeats

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables (optional):
```bash
export PENDO_INTEGRATION_KEY="your-key-here"
export TIMEZONE="America/New_York"
```

3. Ensure MCP servers are configured in Cursor:
   - Atlassian (Jira/Confluence)
   - Glean
   - Pendo

## Usage

### Run as a service:
```bash
python main.py
# or
python scheduler.py
```

**Important:** The scheduler runs as a long-running process. You must **keep that terminal window open** (or run it inside `tmux`/`screen`) for the Monday, daily, and Friday jobs to run on schedule. If you close the terminal or stop the process, no scheduled jobs will run until you start it again.

### Run jobs manually (for testing):
```python
from scheduler import WeeklyUpdateScheduler

scheduler = WeeklyUpdateScheduler()
scheduler.run_now("daily")  # or "monday" or "friday"
```

### Slack (slash command)

You can trigger weekly updates from Slack with the `/weekly-update` slash command.

**Prerequisites**

- A Slack app with a Slash Command whose Request URL points at your running Slack app server (see [SLACK.md](SLACK.md) for setup).

**Environment variables**

- `SLACK_SIGNING_SECRET` (required): From your Slack app → Basic Information → Signing Secret. Used to verify requests.
- `SLACK_BOT_TOKEN` (optional): Only needed if you post follow-up messages via `chat.postMessage` instead of the built-in `response_url`.

**Run the Slack app**

```bash
python slack_app.py
# or: flask --app slack_app run --port 5000
```

Set the slash command Request URL to `https://your-host/slack/weekly-update` (e.g. use [ngrok](https://ngrok.com/) for local testing).

**Usage**

- `/weekly-update` — runs the **daily** update (default).
- `/weekly-update daily` — same.
- `/weekly-update monday` — creates new weekly file (Monday job).
- `/weekly-update friday` — compiles the week (Friday job).

The app responds immediately and runs the job in the background; when the job finishes, it posts a success or failure message to the same channel (if `response_url` was provided by Slack).

**Deploy to Render (so your team can use it without running locally)**

1. Push this repo to GitHub (if it isn’t already).
2. Go to [dashboard.render.com](https://dashboard.render.com) → **New** → **Blueprint**.
3. Connect your GitHub account and select the `weekly_updates_agent` repo. Render will read `render.yaml` and create a free **Web Service**.
4. In the new service, open **Environment** and add:
   - **Key:** `SLACK_SIGNING_SECRET`  
   - **Value:** your Slack app’s Signing Secret (from [api.slack.com](https://api.slack.com/apps) → your app → Basic Information).
   - Add any other env vars your weekly-update job needs on the server (e.g. Confluence/Jira/Glean/Pendo credentials) if you want the background job to run successfully on Render.
5. Deploy (or wait for the first auto-deploy). Once it’s live, copy the service URL (e.g. `https://weekly-updates-slack.onrender.com`).
6. In Slack: [api.slack.com](https://api.slack.com/apps) → your app → **Slash Commands** → edit your command. Set **Request URL** to `https://YOUR-RENDER-URL/slack/weekly-update` (e.g. `https://weekly-updates-slack.onrender.com/slack/weekly-update`). Save.

Anyone in your workspace can then use `/weekly-update` without running anything locally. On the free tier, the service may sleep after ~15 minutes of inactivity; the first request after that may take a few seconds to wake.

## Architecture

- `scheduler.py` - Main scheduler that runs jobs
- `file_manager.py` - Manages Confluence page creation and updates
- `content_generator.py` - Generates content from aggregated data
- `jira_aggregator.py` - Fetches data from Jira
- `glean_aggregator.py` - Fetches data from Glean
- `pendo_aggregator.py` - Fetches data from Pendo
- `granola_aggregator.py` - Fetches meeting data from Granola
- `tone_analyzer.py` - Analyzes past documents for tone/style
- `svp_filter.py` - Filters content for SVP relevance
- `confluence_client.py` - Confluence API wrapper
- `config.py` - Configuration management
- `slack_app.py` - Flask app for Slack slash command (`/weekly-update`)

## Document Structure

Each weekly update includes:
- **Highlights**: Concise summary of major accomplishments and blockers
- **This Week**: Project-level updates and initiative progress
- **Next Week**: Action items and planned next steps
- **Customer Corner**: Links to customer call notes from previous week

## Notes

- The agent uses MCP servers for API access (already configured in Cursor)
- Content is appended incrementally to avoid overwriting existing entries
- Tone and style are learned from past 3-5 weekly documents
- Customer calls are fetched from Granola (primary) or Glean (fallback)
- Granola requires OAuth authentication - you'll need to authenticate when first connecting
