"""
Zoom integration: fetch the latest meeting transcript via Scalekit.

Flow:
  1. zoom_recordings_list  -> recordings that actually exist for the user
  2. pick the newest recording that has a TRANSCRIPT file
  3. actions.request()     -> download the .vtt (Scalekit injects the OAuth token)
  4. parse .vtt            -> plain transcript text
"""

from urllib.parse import urlparse

from scalekit_setup import actions
import config


def _tool_payload(result) -> dict:
    # SDK returns tool output on `.data`; older builds used `.result`. Support both.
    return getattr(result, "data", None) or getattr(result, "result", None) or {}


def _parse_vtt(vtt_text: str) -> str:
    """Strip WEBVTT header, cue numbers, and timestamps; keep spoken lines."""
    lines = []
    for raw in vtt_text.splitlines():
        line = raw.strip()
        if not line or line == "WEBVTT" or "-->" in line or line.isdigit():
            continue
        lines.append(line)
    return "\n".join(lines)


def _find_transcript_file(recording_files: list) -> dict | None:
    for f in recording_files:
        is_transcript = (
            f.get("file_type") == "TRANSCRIPT"
            or f.get("recording_type") == "audio_transcript"
        )
        if is_transcript and f.get("download_url"):
            return f
    return None


def _download_transcript(identifier: str, download_url: str) -> str:
    # Download through the Scalekit Tool Proxy so the vaulted OAuth token is
    # injected automatically. proxy_url for Zoom is https://api.zoom.us, so we
    # pass the download_url's path (+query) relative to that host.
    parsed = urlparse(download_url)
    path = parsed.path + (f"?{parsed.query}" if parsed.query else "")

    print(f"[Zoom] Downloading transcript via Tool Proxy: {path}")
    resp = actions.request(
        connection_name=config.ZOOM_CONNECTION_NAME,
        identifier=identifier,
        method="GET",
        path=path,
    )

    vtt = getattr(resp, "content", None) or getattr(resp, "data", None) or ""
    if isinstance(vtt, bytes):
        vtt = vtt.decode("utf-8", errors="replace")
    if not vtt:
        raise RuntimeError(f"Transcript download returned empty body for {path}")

    return _parse_vtt(vtt)


def fetch_latest_transcript(identifier: str) -> str:
    # Step 1: list cloud recordings for the user (NOT scheduled meetings).
    print("\n[Zoom] Listing cloud recordings...")
    recordings_result = actions.execute_tool(
        tool_name="zoom_recordings_list",
        connection_name=config.ZOOM_CONNECTION_NAME,
        identifier=identifier,
        tool_input={"user_id": "me"},  # optional: {"from": "2026-06-01", "to": "2026-06-30"}
    )

    payload = _tool_payload(recordings_result)
    meetings = payload.get("meetings", [])
    if not meetings:
        raise RuntimeError(
            "No cloud recordings found. Ensure cloud recording + audio "
            "transcription are enabled and the meeting has finished processing."
        )

    # Step 2: newest first; find one carrying a TRANSCRIPT file.
    meetings.sort(key=lambda m: m.get("start_time", ""), reverse=True)
    for meeting in meetings:
        transcript_file = _find_transcript_file(meeting.get("recording_files", []))
        if transcript_file:
            print(f"[Zoom] Transcript found in: {meeting.get('topic')}")
            return _download_transcript(identifier, transcript_file["download_url"])

    raise RuntimeError(
        "Recordings exist but none contain a TRANSCRIPT file. "
        "Enable 'Audio transcript' in Zoom cloud recording settings."
    )
