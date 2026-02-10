# Quick Start Guide

## Setup

1. **Install dependencies:**
```bash
cd weekly_updates_agent
pip install -r requirements.txt
```

2. **Configure MCP Integration:**
   - The agent uses MCP servers configured in Cursor
   - Update `mcp_integration.py` to connect to actual MCP tools
   - See `MCP_INTEGRATION.md` for details

3. **Set environment variables (optional):**
```bash
export PENDO_INTEGRATION_KEY="your-key-here"
export TIMEZONE="America/New_York"
```

## Running the Agent

### As a Scheduled Service
```bash
python main.py
# or
python scheduler.py
```

This will:
- Create new weekly files every Monday at midnight
- Update current weekly file every day at 8pm
- On Fridays at 8:30pm, compile the week into one cohesive document (no dupes)

**Important:** Keep the terminal open (or use `tmux`/`screen`) so the process keeps running. Closing the terminal stops the scheduler and no jobs will run until you start `python main.py` again.

### Manual Execution
```bash
# Run Monday job (create new file)
python main.py --job monday

# Run daily job (update current file)
python main.py --job daily

# Run Friday job (compile week, dedupe)
python main.py --job friday
```

## How It Works

1. **Monday 00:00**: Creates a new weekly update page in Confluence
   - Calculates Friday date of current week
   - Creates page titled "Nick - {Month} {Date}th {Year}"
   - Places in appropriate quarterly folder (Q1 2026, Q2 2026, etc.)
   - Initializes with empty sections

2. **Daily 20:00**: Updates the current week's file
   - Finds most recent weekly page
   - Fetches new data from Jira, Glean, and Pendo
   - Appends new content to appropriate sections
   - Avoids duplicates using content hashing

3. **Friday 20:30**: Compiles the week (runs after daily job)
   - Reads current week's page (which may have repeated sections from daily appends)
   - Merges all Highlights, This Week, Next Week, Customer Corner into one section each
   - Deduplicates bullet points and replaces the page with the compiled doc

## Data Sources

- **Jira**: Your assigned issues, initiatives, blockers
- **Glean**: Project updates, customer call notes
- **Pendo**: Feature usage metrics and activity data

## Content Sections

- **Highlights**: Concise summary (3-5 items) of major accomplishments and blockers
- **This Week**: Project-level updates organized by theme/project
- **Next Week**: Action items and planned next steps
- **Customer Corner**: Links to customer call notes from previous week

## Troubleshooting

### MCP Tools Not Available
- Check that MCP servers are configured in Cursor
- Verify authentication for Atlassian, Glean, and Pendo
- See `MCP_INTEGRATION.md` for integration options

### No Content Generated
- Check that you have assigned Jira issues
- Verify Glean search queries return results
- Ensure Pendo integration key is valid

### Duplicate Content
- The agent uses content hashing to prevent duplicates
- If duplicates appear, check the hash generation logic
- Clear `added_content_hashes` if needed

## Customization

- **Tone**: Modify `tone_analyzer.py` to adjust writing style
- **SVP Filtering**: Update `svp_filter.py` to change relevance criteria
- **Content Generation**: Adjust `content_generator.py` for different formats
- **Scheduling**: Modify times in `scheduler.py` or `config.py`
