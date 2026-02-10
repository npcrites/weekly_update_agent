"""Test script that directly uses MCP tools to generate weekly update for last week."""
import sys
from datetime import datetime, timedelta
from file_manager import FileManager
from content_generator import ContentGenerator
import config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_last_week_friday() -> datetime:
    """Get the Friday date of last week."""
    today = datetime.now()
    last_week = today - timedelta(days=7)
    return config.Config.get_week_friday(last_week)

def get_last_week_start() -> datetime:
    """Get the Monday of last week."""
    friday = get_last_week_friday()
    return friday - timedelta(days=4)

def get_last_week_end() -> datetime:
    """Get the Sunday of last week."""
    return get_last_week_friday()

def generate_test_update():
    """Generate a test weekly update for last week using actual MCP tools."""
    logger.info("Generating test weekly update for last week using MCP tools...")
    
    # Get last week's Friday date
    last_friday = get_last_week_friday()
    last_week_start = get_last_week_start()
    last_week_end = get_last_week_end()
    
    logger.info(f"Target date: {last_friday.strftime('%B %d, %Y')}")
    logger.info(f"Week range: {last_week_start.strftime('%Y-%m-%d')} to {last_week_end.strftime('%Y-%m-%d')}")
    
    # Generate page title
    page_title = config.Config.format_page_title(last_friday)
    logger.info(f"Page title: {page_title}")
    
    # Fetch data using MCP tools directly
    cloud_id = config.Config.JIRA_CLOUD_ID
    
    # Fetch Jira issues
    logger.info("Fetching Jira issues...")
    jira_issues = []
    try:
        jql = f"assignee = currentUser() AND updated >= {last_week_start.strftime('%Y-%m-%d')} ORDER BY updated DESC"
        # Call MCP tool directly - this will work in Cursor environment
        jira_result = mcp_atlassian_searchJiraIssuesUsingJql(
            cloudId=cloud_id,
            jql=jql,
            maxResults=50
        )
        jira_issues = jira_result.get("issues", [])
        logger.info(f"Found {len(jira_issues)} Jira issues")
    except Exception as e:
        logger.warning(f"Error fetching Jira issues: {e}")
    
    # Fetch Glean project updates
    logger.info("Fetching Glean project updates...")
    glean_updates = []
    try:
        query = "project updates initiatives SingleOps migration Kiro Cloudinary performance"
        glean_result = mcp_Glean_search(
            query=query,
            after=last_week_start.strftime("%Y-%m-%d"),
            before=last_week_end.strftime("%Y-%m-%d")
        )
        glean_updates = glean_result.get("results", []) if isinstance(glean_result, dict) else glean_result
        logger.info(f"Found {len(glean_updates)} Glean updates")
    except Exception as e:
        logger.warning(f"Error fetching Glean updates: {e}")
    
    # Fetch customer calls
    logger.info("Fetching customer calls...")
    customer_calls = []
    try:
        meeting_query = f'participants:"Nick Crites" topic:"Customer Call" after:{last_week_start.strftime("%Y-%m-%d")} before:{last_week_end.strftime("%Y-%m-%d")}'
        meetings = mcp_Glean_meeting_lookup(query=meeting_query, extract_transcript="false")
        customer_calls = meetings if isinstance(meetings, list) else []
        logger.info(f"Found {len(customer_calls)} customer calls")
    except Exception as e:
        logger.warning(f"Error fetching customer calls: {e}")
    
    # Fetch Pendo applications
    logger.info("Fetching Pendo data...")
    pendo_apps = []
    try:
        pendo_apps = mcp_Pendo_list_all_applications()
        logger.info(f"Found {len(pendo_apps)} Pendo applications")
    except Exception as e:
        logger.warning(f"Error fetching Pendo data: {e}")
    
    # Generate content sections
    sections = []
    
    # Highlights
    highlights = []
    for issue in jira_issues[:3]:
        key = issue.get("key", "")
        summary = issue.get("fields", {}).get("summary", "")
        status = issue.get("fields", {}).get("status", {}).get("name", "")
        highlights.append(f"* {key}: {summary} ({status})")
    
    if highlights:
        sections.append("## Highlights\n\n" + "\n".join(highlights))
    
    # This Week
    this_week_items = []
    
    # Add initiatives
    initiatives = [i for i in jira_issues if i.get("fields", {}).get("issuetype", {}).get("name") in ["Initiative", "Epic"]]
    if initiatives:
        this_week_items.append("* Team roadmap")
        for init in initiatives[:5]:
            key = init.get("key", "")
            summary = init.get("fields", {}).get("summary", "")
            status = init.get("fields", {}).get("status", {}).get("name", "")
            this_week_items.append(f"    * **{summary}** ({key}) - {status}")
    
    # Add Glean project updates
    if glean_updates:
        this_week_items.append("* Project Updates")
        for update in glean_updates[:5]:
            title = update.get("title", "")
            if title:
                this_week_items.append(f"    * {title}")
    
    if this_week_items:
        sections.append("\n## This Week\n\n" + "\n".join(this_week_items))
    
    # Next Week
    next_week_items = []
    in_progress = [i for i in jira_issues if "progress" in i.get("fields", {}).get("status", {}).get("name", "").lower()]
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
    
    # Combine all sections
    full_content = "\n".join(sections)
    
    # Output results
    print("\n" + "="*80)
    print(f"WEEKLY UPDATE: {page_title}")
    print("="*80)
    print(full_content)
    print("="*80)
    
    # Save to file
    output_file = f"/Users/nickcrites/weekly_updates_agent/test_output_{last_friday.strftime('%Y%m%d')}.md"
    with open(output_file, 'w') as f:
        f.write(f"# {page_title}\n\n")
        f.write(full_content)
    
    logger.info(f"Content saved to: {output_file}")
    
    return {
        "title": page_title,
        "content": full_content,
        "file": output_file,
        "stats": {
            "jira_issues": len(jira_issues),
            "glean_updates": len(glean_updates),
            "customer_calls": len(customer_calls),
            "pendo_apps": len(pendo_apps)
        }
    }

if __name__ == "__main__":
    try:
        result = generate_test_update()
        print(f"\n✅ Successfully generated test update!")
        print(f"📄 File: {result['file']}")
        print(f"\n📊 Stats:")
        print(f"   - Jira issues: {result['stats']['jira_issues']}")
        print(f"   - Glean updates: {result['stats']['glean_updates']}")
        print(f"   - Customer calls: {result['stats']['customer_calls']}")
        print(f"   - Pendo apps: {result['stats']['pendo_apps']}")
    except Exception as e:
        logger.error(f"Error generating test update: {e}", exc_info=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)
