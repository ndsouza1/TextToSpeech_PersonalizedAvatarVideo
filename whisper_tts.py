import whisper
from gtts import gTTS
import soundfile as sf

class WhisperTTS:
    def __init__(self, model_size="base"):
        """Initialize the Whisper model."""
        self.model = whisper.load_model(model_size)

    def transcribe_audio(self, input_audio, output_text_file="transcription.txt"):
        """Transcribes audio and saves text."""
        result = self.model.transcribe(input_audio)
        
        with open(output_text_file, "w") as f:
            f.write(result["text"])
        
        print("\nTranscription Saved:", output_text_file)
        return result["text"]

    def text_to_speech(self, text, output_audio="output.wav"):
        """Converts transcribed text to speech and saves it as WAV."""
        tts = gTTS(text, lang="en")  # Convert text to speech
        tts.save("temp.mp3")  # Save as temporary MP3

        # Convert MP3 to WAV
        data, samplerate = sf.read("temp.mp3")
        sf.write(output_audio, data, samplerate)

        print("\nTTS Audio Saved:", output_audio)

    def process_audio(self, input_audio):
        """Full pipeline: Transcribe and generate speech."""
        transcribed_text = self.transcribe_audio(input_audio)
        print("\nTranscribed Text:\n", transcribed_text)

        output_wav = "transcribed_audio.wav"
        self.text_to_speech(transcribed_text, output_wav)

        return transcribed_text, output_wav

# Usage Example
""" if __name__ == "__main__":
    whisper_tts = WhisperTTS()
    
    input_audio_file = "sample_audio/signal-2025-03-29-153916.mp3"  # Change this to your actual file
    text, wav_file = whisper_tts.process_audio(input_audio_file)

    print("\nFinal Output:\nText File: transcription.txt\nWAV File:", wav_file)
 """