"""Generate weekly update for last week using MCP tools."""
from datetime import datetime, timedelta
import config

def get_last_week_friday():
    """Get the Friday date of last week."""
    today = datetime.now()
    last_week = today - timedelta(days=7)
    return config.Config.get_week_friday(last_week)

def generate_weekly_update():
    """Generate weekly update content."""
    last_friday = get_last_week_friday()
    last_week_start = last_friday - timedelta(days=4)  # Monday
    last_week_end = last_friday  # Friday
    
    page_title = config.Config.format_page_title(last_friday)
    
    print(f"Generating weekly update: {page_title}")
    print(f"Week: {last_week_start.strftime('%Y-%m-%d')} to {last_week_end.strftime('%Y-%m-%d')}\n")
    
    # Fetch data using MCP tools
    cloud_id = config.Config.JIRA_CLOUD_ID
    
    # Get Jira issues
    print("Fetching Jira issues...")
    jira_jql = f"assignee = currentUser() AND updated >= {last_week_start.strftime('%Y-%m-%d')} ORDER BY updated DESC"
    jira_result = mcp_atlassian_searchJiraIssuesUsingJql(
        cloudId=cloud_id,
        jql=jira_jql,
        maxResults=50
    )
    jira_issues = jira_result.get("issues", [])
    print(f"Found {len(jira_issues)} Jira issues\n")
    
    # Get Glean updates
    print("Fetching Glean project updates...")
    glean_result = mcp_Glean_search(
        query="project updates initiatives SingleOps migration Kiro Cloudinary performance",
        after=last_week_start.strftime("%Y-%m-%d"),
        before=last_week_end.strftime("%Y-%m-%d")
    )
    glean_updates = glean_result.get("results", []) if isinstance(glean_result, dict) else []
    print(f"Found {len(glean_updates)} Glean updates\n")
    
    # Get customer calls
    print("Fetching customer calls...")
    meeting_query = f'participants:"Nick Crites" topic:"Customer Call" after:{last_week_start.strftime("%Y-%m-%d")} before:{last_week_end.strftime("%Y-%m-%d")}'
    meetings = mcp_Glean_meeting_lookup(query=meeting_query, extract_transcript="false")
    customer_calls = meetings if isinstance(meetings, list) else []
    print(f"Found {len(customer_calls)} customer calls\n")
    
    # Generate content
    sections = []
    
    # Highlights
    highlights = []
    initiatives = [i for i in jira_issues if i.get("fields", {}).get("issuetype", {}).get("name") in ["Initiative", "Epic"]]
    for init in initiatives[:3]:
        key = init.get("key", "")
        summary = init.get("fields", {}).get("summary", "")
        status = init.get("fields", {}).get("status", {}).get("name", "")
        priority = init.get("fields", {}).get("priority", {}).get("name", "")
        highlights.append(f"* **{summary}** ({key}) - {status}")
    
    blockers = [i for i in jira_issues if i.get("fields", {}).get("priority", {}).get("name") == "Highest"]
    for blocker in blockers[:2]:
        key = blocker.get("key", "")
        summary = blocker.get("fields", {}).get("summary", "")
        highlights.append(f"* Blocker: {summary} ({key})")
    
    if highlights:
        sections.append("## Highlights\n\n" + "\n".join(highlights))
    
    # This Week
    this_week_items = []
    
    if initiatives:
        this_week_items.append("* Team roadmap")
        for init in initiatives[:5]:
            key = init.get("key", "")
            summary = init.get("fields", {}).get("summary", "")
            status = init.get("fields", {}).get("status", {}).get("name", "")
            this_week_items.append(f"    * **{summary}** ({key}) - {status}")
    
    if glean_updates:
        this_week_items.append("* Project Updates")
        for update in glean_updates[:5]:
            title = update.get("title", "")
            snippet = update.get("snippet", "")
            url = update.get("url", "")
            if title:
                this_week_items.append(f"    * {title}")
                if snippet:
                    this_week_items.append(f"        * {snippet[:150]}...")
    
    in_progress = [i for i in jira_issues if "progress" in i.get("fields", {}).get("status", {}).get("name", "").lower()]
    if in_progress:
        this_week_items.append("* Active Work")
        for item in in_progress[:5]:
            key = item.get("key", "")
            summary = item.get("fields", {}).get("summary", "")
            status = item.get("fields", {}).get("status", {}).get("name", "")
            this_week_items.append(f"    * {key}: {summary} ({status})")
    
    if this_week_items:
        sections.append("\n## This Week\n\n" + "\n".join(this_week_items))
    
    # Next Week
    next_week_items = []
    for item in in_progress[:5]:
        key = item.get("key", "")
        summary = item.get("fields", {}).get("summary", "")
        next_week_items.append(f"* Continue work on {key}: {summary}")
    
    if next_week_items:
        sections.append("\n## Next Week\n\n" + "\n".join(next_week_items))
    
    # Customer Corner
    customer_items = []
    for call in customer_calls:
        title = call.get("title", "Customer Call")
        url = call.get("url", "")
        if url:
            customer_items.append(f"{title}\n\n{url}")
        else:
            customer_items.append(title)
    
    if customer_items:
        sections.append("\n## Customer Corner\n\n" + "\n\n".join(customer_items))
    else:
        sections.append("\n## Customer Corner\n\nNo customer calls this week.")
    
    # Combine all sections
    full_content = "\n".join(sections)
    
    # Output
    print("="*80)
    print(f"WEEKLY UPDATE: {page_title}")
    print("="*80)
    print(full_content)
    print("="*80)
    
    # Save to file
    output_file = f"/Users/nickcrites/weekly_updates_agent/weekly_update_{last_friday.strftime('%Y%m%d')}.md"
    with open(output_file, 'w') as f:
        f.write(f"# {page_title}\n\n")
        f.write(full_content)
    
    print(f"\n✅ Saved to: {output_file}")
    
    return {
        "title": page_title,
        "content": full_content,
        "file": output_file
    }

# Generate the update
if __name__ == "__main__":
    result = generate_weekly_update()
