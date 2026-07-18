import config
from jira_agent import file_jira_tickets
from llm_reasoner import reason_over_transcript
from notion_agent import write_notion_summary
from scalekit_setup import ensure_connected
from zoom_agent import fetch_latest_transcript


def process_meeting_for_user(identifier: str) -> None:
    print(f"\n{'=' * 50}")
    print(f"Processing meeting for: {identifier}")
    print(f"{'=' * 50}")

    ensure_connected(config.ZOOM_CONNECTION_NAME, identifier)
    transcript = fetch_latest_transcript(identifier)
    print(f"[Zoom] Transcript fetched (length={len(transcript)})")

    structured = reason_over_transcript(transcript)
    print(f"[LLM] Generated {len(structured['action_items'])} action item(s)")

    ensure_connected(config.NOTION_CONNECTION_NAME, identifier)
    write_notion_summary(identifier, structured)
    print(f"[Notion] Page created: '{structured['title']}'")

    ensure_connected(config.JIRA_CONNECTION_NAME, identifier)
    tickets = file_jira_tickets(identifier, structured["action_items"])
    print(f"[Jira] {len(tickets)} ticket(s) filed")

    print(f"✅ Completed for {identifier}\n")


if __name__ == "__main__":

    print("=" * 50)
    print("Meeting-to-Action Agent")
    print("=" * 50)
    
    try:
        # Fetch transcript (with user selection)
        result = fetch_latest_transcript("Sachin Pal")
        print(f"\n✅ Got recording data:\n{result}")
        
        # TODO: Add reasoning, notion, jira steps
        
    except Exception as e:
        print(f"\n❌ Error:\n{e}")
    # Demo user 1
    # process_meeting_for_user("Sachin Pal")
    # process_meeting_for_user("John Wright")