import multiprocessing
#multiprocessing.set_start_method('spawn', force=True)  # Set before anything else
import os
import uuid
import subprocess
from faster_whisper import WhisperModel
import requests
import time
import threading
import torch
from celery_app import app
from rq import get_current_job

# Ajusta el modelo según tu GPU
MODEL_SIZE = "tiny"
#MODEL_SIZE = "large-v3"
device = "cpu"
compute_type="int8"  # or "float16" for FP16
# or run on GPU with FP16
if torch.cuda.is_available():   
    print ("Using GPU for transcription")
    device = "cuda"
    compute_type = "float16"  # Use FP16 for better performance on GPU
#whisper_model = WhisperModel(MODEL_SIZE, device="cuda", compute_type="float16")
# or run on CPU with INT8
whisper_model = WhisperModel(MODEL_SIZE, device=device, compute_type=compute_type)
DOWNLOAD_FOLDER = "./downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def download_video(url):
    file_id = str(uuid.uuid4())
    output_path = os.path.join(DOWNLOAD_FOLDER, f"{file_id}.mp4")
    subprocess.run(["poetry", "run", "yt-dlp", "-o", output_path, url], check=True)
    return output_path

def run_ffmpeg(video_path, audio_path):
    env = os.environ.copy()
    env["OBJC_DISABLE_INITIALIZE_FORK_SAFETY"] = "YES"
    subprocess.run(
        ["ffmpeg", "-y", "-i", video_path, "-ar", "16000", "-ac", "1", audio_path],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )
def extract_audio(video_path):
    audio_path = video_path.replace(".mp4", ".wav")
    env = os.environ.copy()
    result = subprocess.run(
        ["poetry", "run", "python", "convert_audio.py", video_path],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
    )
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
        
        #job = get_current_job()
        #job.meta['progress'] = "downloading video"
        #job.save_meta()   
        # self.update_state(
        #     state='PROGRESS',
        #     meta={'current': 'downloading video'}
        # )
        # self.update_state(state="PROGRESS")
        video_path = download_video(vimeo_url)
        # self.update_state(
        #     state='PROGRESS',
        #     meta={'current': 'video downloaded'}
        # )        
        # self.update_state(state="DONE")
                
        audio_path = extract_audio(video_path)
        # self.update_state(state="TERMINI")
        # return {'status': 'done'}
        # segments = run_transcription(audio_path)
        # # POST al backend NestJS
        # BACKEND_URL = "https://gencampus-backend-w2ms4.ondigitalocean.app/transcript-segments"
        # payload = {"segments": segments}
        # r = requests.post(f"{BACKEND_URL}/{activity_id}", json=payload)
        # print("NestJS response:", r.status_code, r.text)
        return {'status': 'done'}
        #return {"status": "done", "segments": len(segments)}
    except Exception as e:
        print("ERROR processing job:", e)
        return {"status": "error", "error": str(e)}
    finally:
        #if video_path and os.path.exists(video_path):
            #os.remove(video_path)
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)

