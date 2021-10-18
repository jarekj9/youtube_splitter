import subprocess
import sys, os
import youtube_dl
import pydub
from gooey import Gooey
from gooey import GooeyParser

# INFO variable must have 2 or 3 elements. Adjust ordering of elements to match the file contents.
# TIME and TITLE are neccessary, ARTIST is optional, if downloading compilation! If not in the file, specifiy artist
# separately
TRACKLIST_FILE = "tracklist.txt"  # Text file to be put next to the script!
TEMP_MEDIA_FILE = 'tmp.mp4'
INFO = ["time", "artist", "title"] # what info does the textfile contain and what is the order
SEPARATOR = " - "

# DEMO TEXT FILE - will be created for demo purposes, you should create it yourself for your own video.
# with open(TRACKLIST_FILE, "w") as f:
#     f.write("0:00:00 - My Melancholy Baby\n0:03:58 - Can't Stop Me\n 0:07:42 - Fat Morris\n 0:11:32 - Sometimes\n 0:13:07 - Red Soap\n 0:16:23 - April Showers\n 0:20:52 - By The Rivers\n 0:24:33 - It Don't Mean A Thing\n 0:28:12 - Queen of Hearts\n 0:32:09 - U Can Get It\n 0:36:30 - Not Afraid\n 0:39:47 - Throw It Back (Instrumental)\n 0:42:48 - Downtown Irony\n 0:47:21 - Faidherbe Square\n 0:50:50 - Muhammad Ali")


def time_to_seconds(time_str):
    if len(time_str.split(":")) == 2:
        m, s = time_str.split(':')
        return int(m) * 60 + int(s)
    else:
        h, m, s = time_str.split(':')
        return int(h) * 3600 + int(m) * 60 + int(s)

def download_video(youtube_link: str):
    ydl_opts = {
        'outtmpl': TEMP_MEDIA_FILE,
        'format': 'bestaudio[ext=m4a]',  #'bestvideo[ext=mp4]+bestaudio[ext=m4a]'
        "progress_hooks": [progress_callback]
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        a = ydl.download([youtube_link])

def progress_callback(response):
    if response["status"] == "downloading":
        print('', flush=True)

def split_temp_file(artist_tag, album_tag):

    SAVE_FOLDER = f'{artist_tag} - {album_tag}'

    try:
        with open(TRACKLIST_FILE, "r") as f:
            songs = f.readlines()
            songs = [i.strip("\n").strip("").split(SEPARATOR) for i in songs]
    except FileNotFoundError:
        exit(f'File {TRACKLIST_FILE} is missing.')

    print("Reading source mp3 file ...")
    pydub.AudioSegment.converter = os.getcwd()+ "\\ffmpeg.exe"                    
    pydub.AudioSegment.ffprobe   = os.getcwd()+ "\\ffprobe.exe"
    try:
        sound = pydub.AudioSegment.from_file(os.getcwd() + f"\\{TEMP_MEDIA_FILE}","mp4")
    except FileNotFoundError:
        exit(f'File {TEMP_MEDIA_FILE} is missing.')
    print("Done.")

    if not os.path.exists(SAVE_FOLDER):
        os.mkdir(SAVE_FOLDER)

    for i,j in enumerate(songs):
        print("Converting song no.",i,j)

        artist_song_tag = j[INFO.index("artist")] if "artist" in INFO else artist_tag
        time_start = j[INFO.index("time")]
        title = j[INFO.index("title")]

        time_start = time_to_seconds(time_start)*1000

        if i+1 == len(songs):
            song = sound[time_start:-1]
        else:
            time_finish = time_to_seconds(songs[i+1][INFO.index("time")])*1000-200
            song = sound[time_start:time_finish]

        song.export(os.path.join(SAVE_FOLDER,"{} - {}.mp3".format(artist_tag,title)), format="mp3",
                    tags={"artist":artist_song_tag,"album":album_tag,"title":title, "track": i+1})


@Gooey(show_restart_button=False, progress_regex=r"^\[download\]\s+(\d+\.\d+)%")
def main():
    parser = GooeyParser(description="Program can download youtube music and split it into smaller audio files.")
    parser.add_argument('--link', '-u', help='Youtube URL')
    parser.add_argument("--action", choices=['download_and_process', 'download', 'process'], default='download_and_process',
        help=f"Download only saves {TEMP_MEDIA_FILE} file, which needs to be processed later. ")
    parser.add_argument("--artist_tag", default='Artist', help='Will be used in folder name and mp3 tags in case its missing in tracklist file')
    parser.add_argument("--album_tag", default='The best of', help='Will be used in folder name and mp3 tags')
    parser.add_argument('--version', '-v', action='version', version='%(prog)s 1.0')
    args = parser.parse_args()

    if args.action == 'download_and_process' or args.action == 'download':
        download_video(args.link)
    if args.action == 'download_and_process' or args.action == 'process':
        split_temp_file(args.artist_tag, args.album_tag)

if __name__ == '__main__':
    main()

