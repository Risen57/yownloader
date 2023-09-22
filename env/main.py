from pytube import YouTube
import ffmpeg
import asyncio
import os
import time
from flask import Flask, render_template, request, redirect, url_for, send_file

"""
Please note: I've used a lot of unnecessary comments.
Ik this seems dumb.
It's only so that i remember what I've done if i make any updates in the future.
"""


app = Flask(__name__)
# Async functions have been used to handle multiple requests concurrently

async def download_video(url):
    """
    Video quality doesn't affect audio quality at all, so in order to reduce load on the server,
    the res has been set to 360 since it's available in all videos.
    """
    video = YouTube(url)
    vid_title = video.title
    stream = video.streams.filter(res="360p").first()
    stream.download(filename=f"mp4files/{vid_title}.mp4")


async def convert_mp3(vid_path, vid_title):
    """
    Converts the mp4 file to mp3 since not every yt video has audio streams.
    """
    stream = ffmpeg.input(f"mp4files/{vid_title}.mp4")
    stream = ffmpeg.output(stream, f"mp3files/{vid_title}.mp3")
    ffmpeg.run(stream)


async def delete_files(vid_title):
    """
    Cleans the mp3files/ and mp4files/ dirs in order to reduce server load
    """
    os.remove(f"mp4files/{vid_title}.mp4")
    os.remove(f"mp3files/{vid_title}.mp3")


@app.route("/", methods=["GET", "POST"])
async def hello_world():
    """
    Home Screen
    """
    
    if request.method == "POST":

        # Fetch Video url and title for further use
        vid_url = request.form["target_url"]
        vid_title = YouTube(vid_url).title

        # Download vid as mp4 to the server
        await download_video(vid_url)
        vid_path = f"mp4files/{vid_title}.mp4"

        # Convert to mp3 to be sent as mp3 file
        await convert_mp3(vid_path, vid_title)
        audio_path = f"mp3files/{vid_title}.mp3"

        """
        Send the file and delete it from server.
        This part of the code is confusing since
        it looks like the files get deleted before even sending the file
        but it's not like that.
        It works, don't touch it.
        """
        response = send_file(audio_path, as_attachment=True)
        if response.status_code == 200:
            await delete_files(vid_title)
        return response

    return render_template("index.html")


# if __name__ == "__main__":
#     app.run()
