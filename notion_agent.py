import config
from scalekit_setup import actions


def write_notion_summary(identifier: str, structured: dict) -> dict:
    result = actions.execute_tool(
        tool_name="notion_page_create",
        identifier=identifier,
        connection_name=config.NOTION_CONNECTION_NAME,
        tool_input={
            "database_id": config.NOTION_DATABASE_ID,
            "title": structured["title"],
            "properties": {
                "Summary": structured["summary"],
                "Decisions": "\n".join(structured.get("key_decisions", [])),
            },
        },
    )

    return result.result or {}