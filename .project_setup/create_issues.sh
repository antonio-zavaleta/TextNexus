#!/bin/bash
# --- CONFIGURATION ---
REPO="antonio-zavaleta/TextNexus"  # Target repository for issues
PROJECT_NUMBER="5" # CONFIRMED from URL: users/antonio-zavaleta/projects/5
PLAN_FILE="textnexus_v2_plan.json"
MAPPING_FILE="issue_title_to_number.json"
# ---------------------

# Ensure gh CLI is installed and authenticated
if ! command -v gh &> /dev/null; then
    echo "GitHub CLI (gh) not found. Please install and authenticate."
    exit 1
fi

# Ensure jq is installed
if ! command -v jq &> /dev/null; then
    echo "jq (JSON processor) not found. Please install it."
    exit 1
fi

echo "[]" > $MAPPING_FILE # Initialize JSON array for title-to-number map
chmod +x wire_dependencies.py # Ensure the Python script is executable

echo "--- Starting Issue Creation for TextNexus V2.0 on Project #$PROJECT_NUMBER ---"

# Function to create an issue, add it to the project, and store the mapping
create_issue_and_map() {
    local title=$1
    local body=$2
    local labels=$3
    
    # 1. Create the issue
    OUTPUT=$(gh issue create --title "$title" --body "$body" --repo "$REPO" --label "$labels" 2>&1)
    
    if [ $? -ne 0 ]; then
        echo "Error creating issue: $title"
        echo "$OUTPUT"
        return
    fi
    
    ISSUE_URL=$(echo "$OUTPUT" | grep 'https://github.com/' | tail -n 1)
    ISSUE_NUM=$(basename "$ISSUE_URL")
    
    # 2. Add the created issue to the Project Board
    gh project item-add "$PROJECT_NUMBER" --issue "$ISSUE_URL" > /dev/null 2>&1
    
    echo "Created and added: #$ISSUE_NUM - $title"

    # 3. Add to mapping file
    jq --arg title "$title" --arg num "$ISSUE_NUM" \
        '. += [{"title": $title, "number": ($num | tonumber)}]' "$MAPPING_FILE" > tmp."$MAPPING_FILE" && mv tmp."$MAPPING_FILE" "$MAPPING_FILE"
    
    echo "$ISSUE_NUM"
}

# --- PROCESS JSON HIERARCHY ---
jq -c '.themes[]' "$PLAN_FILE" | while read theme; do
    THEME_TITLE=$(echo "$theme" | jq -r '.title')
    
    jq -c '.epics[]' <<< "$theme" | while read epic; do
        EPIC_TITLE=$(echo "$epic" | jq -r '.title')
        EPIC_BODY="**Parent Theme:** $THEME_TITLE\n\n**Goal:** Major feature area for V2.0."
        EPIC_NUM=$(create_issue_and_map "$EPIC_TITLE" "$EPIC_BODY" "epic,v2.0")
        
        jq -c '.stories[]' <<< "$epic" | while read story; do
            STORY_TITLE=$(echo "$story" | jq -r '.title')
            STORY_LABELS=$(echo "$story" | jq -r '.labels | join(",")')
            STORY_BODY="**Parent Epic:** $EPIC_TITLE (#$EPIC_NUM)\n\n**Goal:** Implement the component/feature (e.g., extend abstract class)."
            STORY_NUM=$(create_issue_and_map "$STORY_TITLE" "$STORY_BODY" "$STORY_LABELS")

            # Store the Parent/Child relationship via comment for easy viewing
            gh issue comment "$STORY_NUM" --repo "$REPO" --body "Parent Epic: #$EPIC_NUM" > /dev/null 2>&1

            # Create Tasks as separate issues
            jq -r '.tasks[]' <<< "$story" | while read task; do
                TASK_TITLE="$task"
                TASK_BODY="**Parent Story:** $STORY_TITLE (#$STORY_NUM)"
                TASK_NUM=$(create_issue_and_map "$TASK_TITLE" "$TASK_BODY" "task,v2.0")

                # Store the Parent/Child relationship via comment
                gh issue comment "$TASK_NUM" --repo "$REPO" --body "Parent Story: #$STORY_NUM" > /dev/null 2>&1
            done
        done
    done
done

echo "--- Issue Creation Complete. ---"
echo "Running Python script to wire dependencies..."

# --- 3. Execute Python Wiring Script ---
# NOTE: The Python script (wire_dependencies.py) must be created and have GITHUB_PAT set.
if [ -f "wire_dependencies.py" ]; then
    python3 wire_dependencies.py
    echo "Dependency wiring complete."
else
    echo "WARNING: wire_dependencies.py not found. Dependencies must be linked manually."
fi
