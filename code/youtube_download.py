import pytube as yt

# https://pytube.io/en/latest/api.html

# import os
# print("Current Working Directory:", os.getcwd())
# os.chdir("test")


def yt2mp3(youtube_video, output_path="audio"):
    try:
        audio_stream = youtube_video.streams.filter(only_audio=True).first()
        audio_stream.download(output_path=output_path)
        print(f"DOWNLOADED -> {youtube_video.title}")
        print(
            f"DOWNLOADED -> {youtube_video.author}, {youtube_video.length},{youtube_video.views}, {youtube_video.rating}"
        )

    except Exception as e:
        print(f"SKIPPED -> {youtube_video.title}")


# get audio from top 3 videos in hit list
for youtube_video in yt.Search("Manolis Kellis Lex Friedman").results[:2]:
    yt2mp3(youtube_video)


# get audio from the top 2 videos in playlist (my playlist). The playlist needs to be PUBLIC
for youtube_video in yt.Playlist(
    "https://www.youtube.com/playlist?list=PLsWyhklHwjExuXrXjJktcdYkCFL0PNdW7"
).videos:
    yt2mp3(youtube_video)


# get audio of specified videos
youtube_video1 = yt.YouTube(
    "https://www.youtube.com/watch?v=JctmnczWg0U"
)  # long URL version
youtube_video2 = yt.YouTube("https://youtu.be/v=cHymMt1SQn8")  # short URL version

yt2mp3(youtube_video1)
yt2mp3(youtube_video2)
