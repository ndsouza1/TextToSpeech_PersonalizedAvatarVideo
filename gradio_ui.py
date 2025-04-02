import gradio as gr
import os
from whisper_tts import WhisperTTS
from ollama_chatbotTTS import OllamaChat
from text_to_speech import TextToSpeech
from sync_audio_video import AudioVideoSync
import re

# Paths
THUMBNAILS_DIR = "thumbnails"
VIDEO_DIR = "sample_video"

# Get available images from the thumbnails folder
def get_thumbnail_images():
    if not os.path.exists(THUMBNAILS_DIR):
        return []
    return [(os.path.splitext(f)[0], os.path.join(THUMBNAILS_DIR, f)) 
            for f in os.listdir(THUMBNAILS_DIR) if f.endswith((".png", ".jpg", ".jpeg"))]

thumbnail_images = get_thumbnail_images()
avatar_names = [name for name, _ in thumbnail_images]  # Extract names for radio buttons

# Function to find the corresponding video
def find_matching_video(file_name):
    file_name = file_name.lower()
    if not os.path.exists(VIDEO_DIR):
        return None

    for video in os.listdir(VIDEO_DIR):
        video_name, ext = os.path.splitext(video)
        if video_name.lower() == file_name and ext in [".mp4", ".avi", ".mov"]:
            video_path = os.path.join(VIDEO_DIR, video)
            print(f"Found Video: {video_path}")  # Print to terminal
            return video_path

    print("No matching video found.")
    return None

# Function to update avatar display
def update_avatar_display(selected_name):
    for name, img_path in thumbnail_images:
        if name == selected_name:
            return img_path
    return None

# Function to check if the process button should be enabled
def check_enable_process_button(selected_name, audio_file, transcribed_text):
    if selected_name and (audio_file or transcribed_text.strip()):
        return gr.update(interactive=True)  # Enable button
    return gr.update(interactive=False)  # Disable button

def process_pipeline(audio_file, transcribed_text, selected_name):
    # Step 1: Transcribe if Audio is Provided
    if audio_file:
        whisper_tts = WhisperTTS()
        transcribed_text = whisper_tts.transcribe_audio(audio_file)
        print(f"Transcribed from Audio: {transcribed_text}")

    # Step 2: Validate Input
    if not transcribed_text or transcribed_text.strip() == "":
        return "Warning: Please provide either an audio file or manually enter text.", "", None, None
    
    # Step 3: Get Chatbot Response
    ollama_chat = OllamaChat()
    chatbot_response = ollama_chat.get_response(transcribed_text)
    chatbot_response = re.sub(r"<think>|</think>", "", chatbot_response).strip()

    if not chatbot_response:
        return transcribed_text, "Warning: Chatbot could not generate a response.", None, None

    # Step 4: Convert Response to Speech
    tts = TextToSpeech()
    output_audio_path = tts.synthesize(chatbot_response)

    print(f"Generated TTS audio file: {output_audio_path}")

    # Step 5: Search for the Corresponding Video
    if not selected_name:
        return transcribed_text, chatbot_response, output_audio_path, "Warning: Please select an avatar."

    input_video = find_matching_video(selected_name.lower())
    if not input_video:
        return transcribed_text, chatbot_response, output_audio_path, "Warning: No matching video found for selected avatar."

    # Step 6: Sync Audio with the Video
    sync = AudioVideoSync()
    output_video_path = sync.sync_audio_video(input_video, output_audio_path)

    return transcribed_text, chatbot_response, output_audio_path, output_video_path

# Define UI Layout
with gr.Blocks() as demo:
    gr.Markdown("## Personalized Avatar Video")

    with gr.Row():
        with gr.Column():
            audio_input = gr.Audio(type="filepath", label="Audio Input", interactive=True)
            transcribed_text_output = gr.Textbox(label="Edit and Process Text", interactive=True)
            chatbot_response_output = gr.Textbox(label="Assistant Response", interactive=False)
            gr.Markdown("### Select an Avatar for Lip Syncing")
            
            with gr.Column():
                selected_avatar = gr.Radio(choices=avatar_names, label="Select an Avatar", interactive=True)
                avatar_display = gr.Image(label="Selected Avatar", interactive=False, width=150, height=150)
            
            process_button = gr.Button("Generate Lip-Sync Video", interactive=False)

        with gr.Column():
            tts_audio_output = gr.Audio(label="Generated Speech", interactive=False)
            video_output = gr.Video(label="Final Lip-Synced Video", interactive=False)

    # Update displayed image when user selects an avatar
    selected_avatar.change(update_avatar_display, inputs=[selected_avatar], outputs=[avatar_display])

    # Check if button should be enabled based on inputs
    selected_avatar.change(check_enable_process_button, inputs=[selected_avatar, audio_input, transcribed_text_output], outputs=[process_button])
    audio_input.change(check_enable_process_button, inputs=[selected_avatar, audio_input, transcribed_text_output], outputs=[process_button])
    transcribed_text_output.change(check_enable_process_button, inputs=[selected_avatar, audio_input, transcribed_text_output], outputs=[process_button])

    process_button.click(
        process_pipeline, 
        inputs=[audio_input, transcribed_text_output, selected_avatar], 
        outputs=[transcribed_text_output, chatbot_response_output, tts_audio_output, video_output]
    )

if __name__ == "__main__":
    demo.launch()
