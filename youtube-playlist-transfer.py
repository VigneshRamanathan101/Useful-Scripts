import os
import googleapiclient.discovery
import googleapiclient.errors
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Scopes required for accessing YouTube API
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

def authenticate():
    """Authenticates the user and returns the YouTube service"""
    creds = None

    if os.path.exists("token.json"):
        creds =  google.auth.credentials.Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("client_secrets.json", SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    # Build and return the YouTube API service
    return googleapiclient.discovery.build("youtube", "v3", credentials=creds)

def copy_playlist(source_playlist_id, target_channel_id):
    """Copies the playlist from the source to the target channel"""
    # Authenticate and get the YouTube service
    youtube = authenticate()

    try:
        # Retrieve the source playlist information
        source_playlist = youtube.playlists().list(
            part="snippet",
            id=source_playlist_id
        ).execute()

        # Extract the playlist details
        playlist_title = source_playlist["items"][0]["snippet"]["title"]
        playlist_description = source_playlist["items"][0]["snippet"]["description"]

        # Create the playlist in the target channel
        new_playlist = youtube.playlists().insert(
            part="snippet",
            body={
                "snippet": {
                    "title": playlist_title,
                    "description": playlist_description
                }
            },
            onBehalfOfContentOwner=target_channel_id
        ).execute()

        # Retrieve the playlist items from the source playlist
        playlist_items = youtube.playlistItems().list(
            part="snippet",
            playlistId=source_playlist_id
        ).execute()

        # Add each playlist item to the newly created playlist
        for item in playlist_items["items"]:
            video_id = item["snippet"]["resourceId"]["videoId"]
            youtube.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": new_playlist["id"],
                        "resourceId": {
                            "kind": "youtube#video",
                            "videoId": video_id
                        }
                    }
                }
            ).execute()

        print("Playlist copied successfully!")

    except googleapiclient.errors.HttpError as e:
        print(f"An error occurred: {e}")

# Replace with the source playlist ID and target channel ID
source_playlist_id = "YOUR_SOURCE_PLAYLIST_ID"
target_channel_id = "YOUR_TARGET_CHANNEL_ID"

# Copy the playlist
copy_playlist(source_playlist_id, target_channel_id)
