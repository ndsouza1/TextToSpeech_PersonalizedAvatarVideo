import os
from TTS.api import TTS
from datetime import datetime

class TextToSpeech:
    def __init__(self, model_name="tts_models/en/ljspeech/vits", device="cpu"):
        """
        Initialize the TTS model.
        :param model_name: The name of the TTS model to use.
        :param device: The device to run the model on ("cuda" for GPU, "cpu" for CPU).
        """
        self.model_name = model_name
        self.device = device
        self.tts = TTS(model_name).to(device)

    def synthesize(self, text, output_dir="output_audio"):
        """
        Convert text to speech and save as a .wav file.
        :param text: The text to convert to speech.
        :param output_dir: Directory to save the audio file.
        :return: The path of the saved audio file.
        """
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Generate output filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if not output_dir.endswith(".wav"):  # Ensure correct file extension
            output_file = os.path.join(output_dir, f"tts_output_{timestamp}.wav")
        else:
            output_file = output_dir

        # Generate speech with custom parameters
        self.tts.tts_to_file(
            text=text,
            file_path=output_file,
            speed=1.4,          # Adjust speed (1.0 = normal)
            noise_scale=0.8,    # Control expressiveness
            noise_scale_w=0.5,  # Control speech rhythm variation
            length_scale=1.1    # Control speech speed and pauses
        )

        print(f"Speech synthesis complete. Saved as {output_file}.")
        return output_file

# Example usage
""" if __name__ == "__main__":
    tts = TextToSpeech()
    text_input = "Hello! This is a test for text-to-speech conversion."
    
    output_path = tts.synthesize(text_input)
    print("\nGenerated Audio File:", output_path) """
