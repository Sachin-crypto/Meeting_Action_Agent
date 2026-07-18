from scalekit import ScalekitClient

import config

sk = ScalekitClient(
    client_id=config.SCALEKIT_CLIENT_ID,
    client_secret=config.SCALEKIT_CLIENT_SECRET,
    env_url=config.SCALEKIT_ENV_URL,
)

actions = sk.actions


def get_connection_status(connection_name: str, identifier: str) -> dict:
    
    resp = actions.get_or_create_connected_account(
        connection_name=connection_name,
        identifier=identifier,
    )
    connected_account = resp.connected_account

    if connected_account.status == "ACTIVE":
        return {"connected": True, "status": "ACTIVE", "authorization_link": None}

    link_resp = actions.get_authorization_link(
        connection_name=connection_name,
        identifier=identifier,
    )
    return {
        "connected": False,
        "status": connected_account.status,
        "authorization_link": link_resp.link,
    }


def ensure_connected(connection_name: str, identifier: str) -> str:
    
    status = get_connection_status(connection_name, identifier)

    if not status["connected"]:
        print(f"\n🔗 Authorize '{connection_name}' for '{identifier}':")
        print(f"   {status['authorization_link']}\n")
        input("   Press Enter after completing OAuth in the browser...")

    return identifier


def discover_tools(connector: str, identifier: str):
    
    tools = actions.search_tools(
        connector=connector,
        identifier=identifier,
        summary=False,
    )
    for tool in tools:
        print(f"- {tool.name}: {tool.description}")
    return tools