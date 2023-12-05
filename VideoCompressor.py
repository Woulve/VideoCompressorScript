import os
import subprocess
from tqdm import tqdm
from PIL import Image

overwriteFiles = False
input_folder = 'C:\\Users\\elias\\Desktop\\handy backup\\Camera'

#Video Settings
videoMaxLongEdge = 1920
videoQuality = 28 # 0-51, lower is better quality
videoFPS = 24

#Image Settings
imageMaxLongEdge = 1920
imageQuality = 70 # 0-100, higher is better quality

def get_file_size(file_path):
    return os.path.getsize(file_path)

def compress_file(input_path, output_path):
    if input_path.endswith('.mp4'):
        compress_video(input_path, output_path)
    elif input_path.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
        compress_image(input_path, output_path)

def compress_image(input_path, output_path):
    if not overwriteFiles and os.path.exists(output_path):
        return
    
    initial_size = get_file_size(input_path)

    with Image.open(input_path) as img:
        width, height = img.size
        if width > height:
            new_width = imageMaxLongEdge
            new_height = int(height * (imageMaxLongEdge / width))
        else:
            new_height = imageMaxLongEdge
            new_width = int(width * (imageMaxLongEdge / height))

        resized_img = img.resize((new_width, new_height), Image.LANCZOS)

        exif_data = resized_img.info.get("exif")
        if exif_data:
            resized_img.save(output_path, quality=imageQuality, exif=exif_data)
        else:
            resized_img.save(output_path, quality=imageQuality)

        input_stat = os.stat(input_path)
        os.utime(output_path, (input_stat.st_atime, input_stat.st_mtime))

        if os.path.exists(output_path):
            saved_space = (initial_size - get_file_size(output_path))
            return saved_space
        else:
            return 0

def compress_video(input_path, output_path):
    if not overwriteFiles and os.path.exists(output_path):
        return
    
    ffmpeg_path = 'C:\\Program Files\\ffmpeg-master-latest-win64-gpl\\bin\\ffmpeg.exe'
    ffmpeg_command = [
        ffmpeg_path,
        '-i', input_path,
        '-c:v', 'libx265',   # Use H.265 codec for video
        '-crf', str(videoQuality),
        '-vf', f'scale=\'if(gt(iw*min({videoMaxLongEdge}/iw,{videoMaxLongEdge}/ih),1920),-2,iw)\':-1', # Scale to max 1920px on long edge
        '-b:a', '96k',       # Lower audio bitrate (96kbit/s)
        '-c:a', 'aac',       # Use AAC codec for audio
        '-r', str(videoFPS),
        '-y',                # Overwrite output file if it exists
        '-strict', 'experimental',
        '-map_metadata', '0',  # Preserve metadata
        output_path
    ]

    subprocess.run(ffmpeg_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if os.path.exists(output_path):
        input_stat = os.stat(input_path)
        os.utime(output_path, (input_stat.st_atime, input_stat.st_mtime))

        initial_size = get_file_size(input_path)
        saved_space = (initial_size - get_file_size(output_path))
        return saved_space
    else:
        return 0

def process_files_in_directory(input_folder):
    converted_video_files = 0
    converted_image_files = 0
    skipped_files = 0
    total_saved_space_videos = 0
    total_saved_space_images = 0

    output_folder_videos = os.path.join(input_folder, 'converted', 'videos')
    output_folder_images = os.path.join(input_folder, 'converted', 'images')

    if not os.path.exists(output_folder_videos):
        os.makedirs(output_folder_videos)

    if not os.path.exists(output_folder_images):
        os.makedirs(output_folder_images)

    for filename in tqdm(os.listdir(input_folder), desc="Converting files"):
        try:
            input_path = os.path.join(input_folder, filename)

            if os.path.isfile(input_path):
                if filename.endswith('.mp4'):
                    output_path = os.path.join(output_folder_videos, filename)
                    saved_space_video = compress_video(input_path, output_path)
                    if saved_space_video == None:
                        print (f"Skipping {filename}")
                        skipped_files += 1
                        continue
                    if saved_space_video == 0:
                        print(f"Failed to convert {filename}")
                        return

                    total_saved_space_videos += saved_space_video
                    converted_video_files += 1
                
                elif filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                    output_path = os.path.join(output_folder_images, filename)
                    saved_space_image = compress_image(input_path, output_path)
                    if saved_space_image == None:
                        print (f"Skipping {filename}")
                        skipped_files += 1
                        continue
                    if saved_space_image == 0:
                        print(f"Failed to convert {filename}")
                        return

                    total_saved_space_images += saved_space_image
                    converted_image_files += 1
        except (KeyboardInterrupt, SystemExit):  # Handling exit cases
            if os.path.exists(output_path):
                print(f"Removing {output_path}")
                os.remove(output_path)
            raise

        except Exception as e:  # Catching other exceptions
            print(f"Error during compression: {e}")
            if os.path.exists(output_path):
                os.remove(output_path)
            return 0

    print(f"Converted {converted_video_files} video files. Saved {total_saved_space_videos / 1e6:.2f} MB.")
    print(f"Converted {converted_image_files} image files. Saved {total_saved_space_images / 1e6:.2f} MB.")
    print(f"Skipped {skipped_files} files.")

process_files_in_directory(input_folder)
