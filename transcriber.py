import os
import uuid
import subprocess
from faster_whisper import WhisperModel
import requests

# Ajusta el modelo según tu GPU
MODEL_SIZE = "tiny"
whisper_model = WhisperModel(MODEL_SIZE, device="cuda", compute_type="float16")
DOWNLOAD_FOLDER = "./downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def download_video(url):
    file_id = str(uuid.uuid4())
    output_path = os.path.join(DOWNLOAD_FOLDER, f"{file_id}.mp4")
    subprocess.run(["yt-dlp", "-o", output_path, url], check=True)
    return output_path

def extract_audio(video_path):
    audio_path = video_path.replace(".mp4", ".wav")
    subprocess.run(["ffmpeg", "-y", "-i", video_path, "-ar", "16000", "-ac", "1", audio_path], check=True)
    return audio_path

def run_transcription(audio_path):
    segments, info = whisper_model.transcribe(audio_path)
    result = []
    for s in segments:
        result.append({
            "startTime": float(s.start),
            "endTime": float(s.end),
            "text": s.text
        })
    return result

def process_job(vimeo_url, activity_id):
    video_path = None
    audio_path = None
    try:
        video_path = download_video(vimeo_url)
        audio_path = extract_audio(video_path)
        segments = run_transcription(audio_path)
        # POST al backend NestJS
        BACKEND_URL = "https://gencampus-backend-w2ms4.ondigitalocean.app/transcript-segments"
        payload = {"segments": segments}
        r = requests.post(f"{BACKEND_URL}/{activity_id}", json=payload)
        print("NestJS response:", r.status_code, r.text)
        return {"status": "done", "segments": len(segments)}
    except Exception as e:
        print("ERROR processing job:", e)
        return {"status": "error", "error": str(e)}
    finally:
        if video_path and os.path.exists(video_path):
            os.remove(video_path)
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)

