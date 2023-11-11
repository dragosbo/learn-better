# use dragos env
# pip install scrapetube youtube_transcript_api  # versions 2.5.1 and 0.6.1
# pip install google-api-python-client
# see discussion on POE for how to do things https://poe.com/chat/2q2pe5p5u9rht1f6za8
import os
import json
import googleapiclient.discovery
import scrapetube
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    NoTranscriptFound,
    NoTranscriptAvailable,
    TranscriptsDisabled,
)


def save_file(filepath, content):
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)


def get_channel_id(yt, username):
    request = yt.channels().list(part="snippet", forUsername=username)
    response = request.execute()
    channel_id = response["items"][0]["id"]
    return channel_id


def get_playlists(yt, channel_id):
    request = yt.playlists().list(part="snippet", channelId=channel_id, maxResults=50)
    response = request.execute()
    playlists = {i["snippet"]["title"]: i["id"] for i in response["items"]}
    return playlists


def get_transcripts(playlist):
    videos = scrapetube.get_playlist(playlist)
    transcripts = {}
    no_transcripts = {}
    for v in videos:
        try:
            title = v["title"]["runs"][0]["text"]
            print(title)
            clean_title = "".join(
                c for c in title if c not in list(';:][*|?<>/"()')
            )  # remove special chars

            filename = f"timestamped/{clean_title}.txt"
            if not os.path.exists(filename):
                text = YouTubeTranscriptApi.get_transcript(
                    v["videoId"], languages=["en", "fr"]
                )
                transcript = " ".join([i["text"] for i in text])
                save_file(filename, transcript)
            transcripts[v["videoId"]] = title

        # except FileNotFoundError:
        #     print(f"Error: File not found.", filename)
        # except NoTranscriptFound:
        #     print(
        #         f"'No transcripts were found for any of the requested language codes'",
        #         title,
        #     )
        # except NoTranscriptAvailable:
        #     print(f"No transcripts are available for this video", title)
        except TranscriptsDisabled:
            print(f"    {title} <---- Subtitles are disabled for this video")
            no_transcripts[v["videoId"]] = title
        except Exception as err:
            # msg = "NO TRANSCRIPT AVAILABLE - " + title
            no_transcripts[v["videoId"]] = title
            print(title)
            print("Error:", str(err))

    return transcripts, no_transcripts


# ------------------------ MAIN ---------------------------

# Read the JSON file
with open("secrets.json") as file:
    config = json.load(file)

# Create the YouTube Data API client
yt = googleapiclient.discovery.build(
    "youtube", "v3", developerKey=config["YOUTUBE_API_KEY"]
)

user_name = "dragosboros"
channel_id = get_channel_id(yt, user_name)
playlists = get_playlists(yt, channel_id)

# playlist = playlists["Obsidian"]

transcripts = {}
no_transcripts = {}
for p in playlists:
    print("PROCESSING PLAYLIST ---", p)
    transcripts[p], no_transcripts[p] = get_transcripts(playlists[p])

JSON = {
    "user_name": user_name,
    "channel_id": channel_id,
    "public playlists": playlists,
    "transcripts": transcripts,
    "no_transcripts": no_transcripts,
}

with open("dragos_youtube.json", "w") as file:
    json.dump(JSON, file, indent=4)

# how to avoid writing a file if it already exists


print("DONE")

# based on my username

# videos = scrapetube.get_playlist("PLsWyhklHwjEytvT9IVL071NaURpyZmbnF")

# https://pypi.org/project/scrapetube/
# YOU HAVE TO MAKE THE PLAYLIST PUBLIC

# https://studio.youtube.com/channel/UCtXMX2QDtGA__BoLNIu4o5w/music  - on my channel there is a lot of music in the audio library


# https://www.youtube.com/handle
# https://www.youtube.com/channel/UCtXMX2QDtGA__BoLNIu4o5w  - this is mychannel
# https://www.youtube.com/@dragosborosgpt
# https://www.youtube.com/@dragosboros_rapid  - my channel
# https://www.youtube.com/@dragosborosgpt/playlists
# ONLY PUBLIC PLAYLISTS are displayed

# https://www.googleapis.com/youtube/v3/channels?part=snippet&forUsername=dragosboros&key=AIzaSyCCVAM49Ol_x0kzroD0ILP4-E4xmhP6nJ8
# https://stackoverflow.com/questions/75841604/i-cant-get-channel-id-using-youtube-data-api-v3#:~:text=Nevertheless%20you%20can%20retrieve%20channel,get%20the%20associated%20channel%20id.
