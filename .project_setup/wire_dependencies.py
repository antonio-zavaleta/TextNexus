import json
import os
import requests # Requires: poetry add requests

# 1. Configuration (Set GITHUB_PAT env var before running)
GITHUB_PAT = os.environ.get("GITHUB_PAT")
REPO_OWNER = "antonio-zavaleta"
REPO_NAME = "TextNexus"
MAPPING_FILE = "issue_title_to_number.json"
PLAN_FILE = "textnexus_v2_plan.json"
API_URL = "https://api.github.com/graphql"

if not GITHUB_PAT:
    raise ValueError("GITHUB_PAT environment variable not set.")

def get_headers():
    """Returns the authorization headers for the GraphQL API."""
    return {
        "Authorization": f"bearer {GITHUB_PAT}",
        "Content-Type": "application/json",
    }

def get_issue_node_id(issue_number):
    """
    Retrieves the global Node ID (required for GraphQL mutations) for an issue number.
    This function requires a GraphQL query to fetch the ID using the issue number.
    """
    # *** IMPLEMENTATION REQUIRED HERE ***
    # This involves sending a GraphQL query to retrieve the Node ID.
    pass 

def create_dependency(blocked_issue_id, blocking_issue_id):
    """
    Creates an 'IS_BLOCKED_BY' link using a GraphQL mutation.
    """
    # *** IMPLEMENTATION REQUIRED HERE ***
    # This involves sending a GraphQL mutation using the 'addProjectV2ItemDependency'
    # or similar mutation to link the Node IDs.
    pass 

def run_wiring():
    # 1. Load issue mapping (Title -> Number)
    try:
        with open(MAPPING_FILE, 'r') as f:
            issue_map_list = json.load(f)
        title_to_num = {item['title']: item['number'] for item in issue_map_list}
    except FileNotFoundError:
        print(f"Error: Mapping file '{MAPPING_FILE}' not found. Run create_issues.sh first.")
        return

    # 2. Load the plan to get dependency array
    with open(PLAN_FILE, 'r') as f:
        plan = json.load(f)

    print("--- Starting Dependency Wiring (IS BLOCKED BY) ---")
    
    # 3. Find and link dependencies
    for theme in plan['themes']:
        for epic in theme['epics']:
            for story in epic['stories']:
                story_title = story['title']
                dependencies = story.get('dependencies', [])
                
                if not dependencies:
                    continue

                for dependency_title in dependencies:
                    # Get issue numbers
                    blocker_num = title_to_num.get(dependency_title)
                    blocked_num = title_to_num.get(story_title)

                    if blocker_num and blocked_num:
                        print(f"Wiring: {story_title} (#_{blocked_num}) IS BLOCKED BY {dependency_title} (#_{blocker_num})")
                        
                        # Fetch Node IDs (critical step requiring API calls)
                        # blocked_id = get_issue_node_id(blocked_num) 
                        # blocker_id = get_issue_node_id(blocker_num)
                        
                        # Example: create_dependency(blocked_id, blocker_id)
                    else:
                        print(f"WARNING: Could not find issue number for one or both titles: {story_title}, {dependency_title}")

if __name__ == "__main__":
    run_wiring()
