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
