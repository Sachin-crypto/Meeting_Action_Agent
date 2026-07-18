"""
Zoom integration: fetch meeting transcript using Scalekit.
"""

# from scalekit_setup import actions
# import config


# def fetch_latest_transcript(identifier: str) -> str:
#     """
#     Fetch latest Zoom recording transcript using Scalekit.
#     """
    
#     print("[Zoom] Fetching latest recordings...")
    
#     # Get latest recordings
#     result = actions.execute_tool(
#         tool_input={"meeting_id": "764 8394 7356"},
#         tool_name="zoom_meeting_recordings_get",
#         connection_name=config.ZOOM_CONNECTION_NAME,
#         identifier=identifier,
#     )
    
#     print(f"[Zoom] Full response: {result}")
#     print(f"[Zoom] Result data: {result.result}")
    
#     # Check what we got back
#     payload = result.result or {}
#     recording_files = payload.get("recording_files", [])

#     for file in recording_files:
#         if file.get("file_type") in ("TIMELINE", "TRANSCRIPT") or file.get(
#             "recording_type"
#         ) == "audio_transcript":
#             transcript = file.get("file_content") or file.get("download_url", "")
#             if transcript:
#                 return transcript

#     raise RuntimeError(
#         "No transcript found in the latest recording. "
#         "Ensure cloud recording and transcription are enabled."
#     )



"""
Zoom integration: List meetings, select one, get its recordings
Using exact Scalekit tool names from docs
"""

from scalekit_setup import actions
import config


def fetch_latest_transcript(identifier: str) -> str:
    """
    Step 1: List meetings
    Step 2: User selects meeting
    Step 3: Get recordings for that meeting
    """
    
    print("\n[Zoom] Step 1: Fetching your meetings...")
    
    # Step 1: List all meetings
    meetings_result = actions.execute_tool(
        tool_input={
            "user_id": "me",
            "type": "scheduled"
        },
        tool_name="zoom_meetings_list",
        connection_name=config.ZOOM_CONNECTION_NAME,
        identifier=identifier,
    )
    
    payload = meetings_result.result or {}
    meetings = payload.get("meetings", [])
    
    if not meetings:
        raise RuntimeError("❌ No scheduled meetings found")
    
    print(f"\n✅ Found {len(meetings)} meetings:\n")
    
    # Show list to user
    for i, meeting in enumerate(meetings, 1):
        print(f"{i}. {meeting.get('topic')} ({meeting.get('start_time')})")
    
    # User selects meeting
    print()
    choice = input(f"Select meeting (1-{len(meetings)}): ").strip()
    
    try:
        idx = int(choice) - 1
        if idx < 0 or idx >= len(meetings):
            raise ValueError()
        selected_meeting = meetings[idx]
    except (ValueError, IndexError):
        raise RuntimeError("❌ Invalid selection")
    
    meeting_id = selected_meeting.get("id")
    print(f"\n✅ Selected: {selected_meeting.get('topic')}")
    
    # Step 2: Get recordings for this meeting
    print(f"\n[Zoom] Step 2: Fetching recordings for meeting {meeting_id}...")
    
    recordings_result = actions.execute_tool(
        tool_input={
            "meeting_id": meeting_id
        },
        tool_name="zoom_meeting_recordings_get",
        connection_name=config.ZOOM_CONNECTION_NAME,
        identifier=identifier,
    )
    
    print(f"[DEBUG] Recordings response: {recordings_result}")
    
    recordings_data = recordings_result.result or {}
    recordings = recordings_data.get("recording_files", [])
    
    if not recordings:
        raise RuntimeError(f"❌ No recordings found for this meeting")
    
    print(f"✅ Found {len(recordings)} recording file(s)")
    
    # Return first recording (or show list if multiple)
    first_recording = recordings[0]
    
    return str(first_recording)