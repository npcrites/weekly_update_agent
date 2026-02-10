# MCP Integration Notes

## Overview

This agent is designed to work with MCP (Model Context Protocol) servers that are configured in Cursor. The actual MCP tool calls are abstracted through the `mcp_integration.py` module.

## Current Implementation

The `mcp_integration.py` module provides placeholder methods that would need to be connected to actual MCP tool calls. In a Cursor environment, these would be direct MCP tool invocations.

## MCP Tools Used

### Atlassian (Jira/Confluence)
- `mcp_atlassian_searchJiraIssuesUsingJql` - Search Jira issues
- `mcp_atlassian_getConfluencePage` - Get Confluence page content
- `mcp_atlassian_createConfluencePage` - Create new Confluence pages
- `mcp_atlassian_updateConfluencePage` - Update existing pages
- `mcp_atlassian_getConfluencePageDescendants` - Get child pages

### Glean
- `mcp_Glean_search` - Search Glean documents
- `mcp_Glean_meeting_lookup` - Lookup meeting transcripts

### Pendo
- `mcp_Pendo_list_all_applications` - List Pendo applications
- Note: `activityQuery` may not be available - check available Pendo MCP tools

## Integration Options

### Option 1: Cursor Environment
When running in Cursor, MCP tools are available directly. You can modify `mcp_integration.py` to call them directly:

```python
# Example for Jira
def get_jira_issues(cloud_id: str, jql: str, max_results: int = 50):
    # Direct MCP call in Cursor
    return mcp_atlassian_searchJiraIssuesUsingJql(
        cloudId=cloud_id,
        jql=jql,
        maxResults=max_results
    )
```

### Option 2: Standalone with MCP Client
For standalone execution, you would need an MCP client library:

```python
from mcp import Client

client = Client("atlassian")
result = client.call_tool("searchJiraIssuesUsingJql", {
    "cloudId": cloud_id,
    "jql": jql,
    "maxResults": max_results
})
```

### Option 3: HTTP API Wrapper
Some MCP servers expose HTTP endpoints. You could create HTTP clients for those.

## Testing

To test the agent without full MCP integration, you can:
1. Mock the MCP integration methods
2. Use test data in the aggregators
3. Run individual components in isolation

## Next Steps

1. Connect `mcp_integration.py` to actual MCP tool calls based on your environment
2. Test with real data from Jira, Glean, and Pendo
3. Adjust queries and data processing based on actual API responses
