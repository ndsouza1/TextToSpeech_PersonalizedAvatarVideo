import os
import subprocess

def generate_thumbnails(video_folder, thumbnail_folder, timestamp="00:00:05"):
    if not os.path.exists(thumbnail_folder):
        os.makedirs(thumbnail_folder)
    
    for video_file in os.listdir(video_folder):
        video_path = os.path.join(video_folder, video_file)
        
        if os.path.isfile(video_path) and video_file.lower().endswith((".mp4", ".mkv", ".avi", ".mov", ".flv")):
            thumbnail_name = os.path.splitext(video_file)[0] + ".png"
            thumbnail_path = os.path.join(thumbnail_folder, thumbnail_name)
            
            command = [
                "ffmpeg", "-i", video_path,
                "-ss", timestamp, "-vframes", "1", "-q:v", "2",
                thumbnail_path
            ]
            
            try:
                subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                print(f"Thumbnail generated: {thumbnail_path}")
            except subprocess.CalledProcessError as e:
                print(f"Error generating thumbnail for {video_file}: {e}")

if __name__ == "__main__":
    video_folder = "sample_video"  # Change to your video folder path
    thumbnail_folder = "thumbnails"
    generate_thumbnails(video_folder, thumbnail_folder)