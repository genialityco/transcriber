from flask import Flask, request, jsonify
from redis import Redis
from rq import Queue
import subprocess
import os
import platform

if platform.system() == "Darwin":  # macOS
    from celery_tasks import transcribe

    result = transcribe.delay("./example.mp4")
    print("Celery task submitted:", result.id)
else:
    import redis
    from rq import Queue
    from tasks import rq_tasks

app = Flask(__name__)

redis_conn = Redis()
q = Queue(connection=redis_conn)


@app.route("/enqueue", methods=["POST"])
def enqueue():
    data = request.json
    vimeo_url = data.get("vimeo_url")
    activity_id = data.get("activity_id")

    if not vimeo_url or not activity_id:
        return jsonify({"error": "Missing vimeo_url or activity_id"}), 400

    taskid = 0
    if platform.system() == "Darwin":  # macOS
        from celery_tasks import extract_audio

        result = transcribe.delay(vimeo_url, activity_id)
        print("Celery task submitted:", result.id)
        taskid = result.id
    else:
        import redis
        from rq import Queue
        from rq_tasks import transcribe_rq

        q = Queue(connection=redis.from_url("redis://localhost:6379/0"))
        job = q.enqueue(transcribe_rq, vimeo_url, activity_id)
        print("RQ job submitted:", job.id)
        taskid = result.id
    # job = q.enqueue(process_job, vimeo_url, activity_id)
    # job.meta['progress'] = 'niguno'
    # job.save_meta()
    # extract_audio('./downloads/637aa0c7-4fba-425d-b98a-7e0f29d477ff.mp4')
    # job.meta['progress'] = 'finished'
    # job.save_meta()
    return jsonify({"job_id": taskid, "status": "queued"})


@app.route("/status/<job_id>", methods=["GET"])
def status(job_id):
    job = q.fetch_job(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    if job.is_finished:
        return jsonify({"status": "done", "result": job.result})
    elif job.is_failed:
        return jsonify({"status": "error"})
    else:
        return jsonify({"status": job.get_status()})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
