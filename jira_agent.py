import config
from scalekit_setup import actions


def file_jira_tickets(identifier: str, action_items: list) -> list:
    created = []

    for item in action_items:
        summary = f"{item.get('owner', 'Unassigned')}: {item['task']}"
        result = actions.execute_tool(
            tool_name="jira_create_issue",
            identifier=identifier,
            connection_name=config.JIRA_CONNECTION_NAME,
            tool_input={
                "project_key": config.JIRA_PROJECT_KEY,
                "summary": summary,
                "description": item["task"],
                "labels": ["meeting-action", "auto"],
                **({"due_date": item["due_date"]} if item.get("due_date") else {}),
            },
        )
        # SDK returns tool output on `.data`; older builds used `.result`.
        payload = getattr(result, "data", None) or getattr(result, "result", None)
        created.append(payload or {"summary": summary})

    return created