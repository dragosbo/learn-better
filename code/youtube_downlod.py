import pytube as yt

# import os
# print("Current Working Directory:", os.getcwd())
# os.chdir("test")


def yt2mp3(video):
    try:
        video.streams.filter(only_audio=True).first().download("audio")
        print(f"DOWNLOAD -> {video.title}")

    except Exception as e:
        print(f"SKIP -> {video.title}")


# get audio from top 2 videos in hit list
for video in yt.Search("Manolis Kellis Lex Friedman").results[:2]:
    yt2mp3(video)

# get audio of specified video
yt2mp3(yt.YouTube("https://youtu.be/s-PKj3eUT9k"))
# https://www.youtube.com/watch?v=JctmnczWg0U