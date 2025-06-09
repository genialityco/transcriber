import os
import subprocess
from celery_app import celery_app
from transcriber import process_job;
@celery_app.task(name="transcribe")
def transcribe(vimeo_url, activity_id):
    #self.update_state(state="PROGRESS")
    return process_job(vimeo_url, activity_id)