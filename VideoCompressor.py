import os
import subprocess
from datetime import datetime
from PIL import Image

overwriteFiles = False
input_folder = 'C:\\Users\\elias\\Desktop\\handy backup\\Neuer Ordner'

#Video Settings
videoMaxLongEdge = 1920
videoQuality = 28 # 0-51, lower is better quality
videoFPS = 24

#Image Settings
imageMaxLongEdge = 1920
imageQuality = 70 # 0-100, higher is better quality

def compress_file(input_path, output_path):
    if input_path.endswith('.mp4'):
        compress_video(input_path, output_path)
    elif input_path.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
        compress_image(input_path, output_path)

def compress_image(input_path, output_path):
    if not overwriteFiles and os.path.exists(output_path):
        return

    with Image.open(input_path) as img:
        width, height = img.size
        if width > height:
            new_width = imageMaxLongEdge
            new_height = int(height * (imageMaxLongEdge / width))
        else:
            new_height = imageMaxLongEdge
            new_width = int(width * (imageMaxLongEdge / height))

        resized_img = img.resize((new_width, new_height), Image.LANCZOS)

        resized_img.save(output_path, quality=imageQuality, exif=resized_img.info.get("exif"))


def compress_video(input_path, output_path):
    if not overwriteFiles and os.path.exists(output_path):
        return
    
    ffmpeg_path = 'C:\\Program Files\\ffmpeg-master-latest-win64-gpl\\bin\\ffmpeg.exe'
    ffmpeg_command = [
        ffmpeg_path,
        '-i', input_path,
        '-c:v', 'libx265',   # Use H.265 codec for video
        '-crf', videoQuality,
        '-vf', f'scale=\'if(gt(iw*min({videoMaxLongEdge}/iw,{videoMaxLongEdge}/ih),{videoMaxLongEdge},-2)\':-1',  # Resize based on the maximum long edge
        '-b:a', '96k',       # Lower audio bitrate (96kbit/s)
        '-c:a', 'aac',       # Use AAC codec for audio
        '-r', videoFPS,
        '-y',                # Overwrite output file if it exists
        '-strict', 'experimental',
        '-map_metadata', '0',  # Preserve metadata
        output_path
    ]

    subprocess.run(ffmpeg_command)

def process_files_in_directory(input_folder):
    output_folder_videos = os.path.join(input_folder, 'converted', 'videos')
    output_folder_images = os.path.join(input_folder, 'converted', 'images')

    if not os.path.exists(output_folder_videos):
        os.makedirs(output_folder_videos)

    if not os.path.exists(output_folder_images):
        os.makedirs(output_folder_images)

    for filename in os.listdir(input_folder):
        input_path = os.path.join(input_folder, filename)

        if os.path.isfile(input_path):
            if filename.endswith('.mp4'):
                output_path = os.path.join(output_folder_videos, filename)
                compress_video(input_path, output_path)
            elif filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                output_path = os.path.join(output_folder_images, filename)
                compress_image(input_path, output_path)

process_files_in_directory(input_folder)
