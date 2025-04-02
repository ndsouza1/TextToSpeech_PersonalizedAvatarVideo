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

def get_thumbnail_images():
    if not os.path.exists(THUMBNAILS_DIR):
        return []
    return [(os.path.splitext(f)[0], os.path.join(THUMBNAILS_DIR, f)) 
            for f in os.listdir(THUMBNAILS_DIR) if f.endswith((".png", ".jpg", ".jpeg"))]

thumbnail_images = get_thumbnail_images()
avatar_names = [name for name, _ in thumbnail_images]

def find_matching_video(file_name):
    file_name = file_name.lower()
    if not os.path.exists(VIDEO_DIR):
        return None
    for video in os.listdir(VIDEO_DIR):
        video_name, ext = os.path.splitext(video)
        if video_name.lower() == file_name and ext in [".mp4", ".avi", ".mov"]:
            return os.path.join(VIDEO_DIR, video)
    return None

def update_avatar_display(selected_name):
    for name, img_path in thumbnail_images:
        if name == selected_name:
            return img_path
    return None

def check_enable_process_button(selected_name, audio_file, transcribed_text):
    if selected_name and (audio_file or transcribed_text.strip()):
        return gr.update(interactive=True)
    return gr.update(interactive=False)

def process_pipeline(audio_file, transcribed_text, selected_name):
    if audio_file:
        whisper_tts = WhisperTTS()
        transcribed_text = whisper_tts.transcribe_audio(audio_file)
        yield transcribed_text, "", None, None  # Show transcribed text first
    
    if not transcribed_text.strip():
        yield "Warning: Please provide valid text.", "", None, None
        return
    
    ollama_chat = OllamaChat()
    chatbot_response = ollama_chat.get_response(transcribed_text)
    chatbot_response = re.sub(r"<think>|</think>", "", chatbot_response).strip()
    yield transcribed_text, chatbot_response, None, None  # Show chatbot response next

    if not chatbot_response:
        yield transcribed_text, "Warning: No chatbot response.", None, None
        return

    tts = TextToSpeech()
    output_audio_path = tts.synthesize(chatbot_response)
    yield transcribed_text, chatbot_response, output_audio_path, None  # Show generated speech

    if not selected_name:
        yield transcribed_text, chatbot_response, output_audio_path, "Warning: Select an avatar."
        return

    input_video = find_matching_video(selected_name.lower())
    if not input_video:
        yield transcribed_text, chatbot_response, output_audio_path, "Warning: No matching video."
        return

    sync = AudioVideoSync()
    output_video_path = sync.sync_audio_video(input_video, output_audio_path)
    yield transcribed_text, chatbot_response, output_audio_path, output_video_path  # Show final video

with gr.Blocks() as demo:
    gr.Markdown("## Personalized Avatar Video")

    with gr.Row():
        with gr.Column():
            audio_input = gr.Audio(type="filepath", label="Audio Input")
            transcribed_text_output = gr.Textbox(label="Edit and Process Text")
            chatbot_response_output = gr.Textbox(label="Assistant Response")
            gr.Markdown("### Select an Avatar")
            selected_avatar = gr.Radio(choices=avatar_names, label="Select an Avatar")
            avatar_display = gr.Image(label="Selected Avatar", width=150, height=150)
            process_button = gr.Button("Generate Lip-Sync Video", interactive=False)
        
        with gr.Column():
            tts_audio_output = gr.Audio(label="Generated Speech")
            video_output = gr.Video(label="Final Lip-Synced Video")

    selected_avatar.change(update_avatar_display, inputs=[selected_avatar], outputs=[avatar_display])
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
