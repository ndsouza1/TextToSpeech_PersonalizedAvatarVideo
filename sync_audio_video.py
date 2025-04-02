import torch
import gc
import os
import subprocess
import datetime

class AudioVideoSync:
    def __init__(self, wav2lip_dir="Wav2Lip"):
        self.wav2lip_dir = wav2lip_dir
        self.checkpoint_path = os.path.join(wav2lip_dir, "checkpoints", "wav2lip_gan.pth")

    def print_memory_usage(self, stage=""):
        """Prints GPU memory usage at different stages."""
        os.system('nvidia-smi')
        print(f"[{stage}] Allocated Memory: {torch.cuda.memory_allocated() / 1024**2:.2f} MB")
        print(f"[{stage}] Reserved Memory: {torch.cuda.memory_reserved() / 1024**2:.2f} MB")
        print("-" * 50)

    def sync_audio_video(self, video_path, audio_path, output_video=None):
        """Syncs audio and video using Wav2Lip."""
        if not os.path.exists(video_path) or not os.path.exists(audio_path):
            raise FileNotFoundError("Video or Audio file not found.")

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        result_video = output_video or f"result_{timestamp}.mp4"

        #  Before running Wav2Lip, clear cache and check memory
        gc.collect()
        torch.cuda.empty_cache()
        self.print_memory_usage("Before Wav2Lip Inference")

        #  Run Wav2Lip
        # Run Wav2Lip inference with more accurate lip sync
        print("Running Wav2Lip for better lip movement...")
        result = subprocess.run([
            "python", os.path.join(self.wav2lip_dir, "inference.py"),
            "--checkpoint_path", self.checkpoint_path,
            "--face", video_path,
            "--audio", audio_path,
            "--outfile", result_video,
            "--wav2lip_batch_size", "1",
            "--resize_factor", "2",  # Better accuracy for lips
            "--nosmooth"  # Ensures smoother transitions
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if result.returncode != 0:
            print("Error in Wav2Lip inference:", result.stderr.decode())
            return None

        #  After inference, free memory
        gc.collect()
        torch.cuda.empty_cache()
        self.print_memory_usage("After Wav2Lip Inference")

        print(f" Output saved at: {result_video}")
        return result_video

