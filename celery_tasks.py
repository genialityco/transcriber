import os
import subprocess
from celery_app import app
from transcriber import process_job;
@app.task(bind=True)
def transcribe(self,vimeo_url, activity_id):
    self.update_state(state="PROGRESS")
    return process_job(vimeo_url, activity_id)