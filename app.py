from flask import Flask, request, jsonify
from redis import Redis
from rq import Queue
from transcriber import process_job

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
    job = q.enqueue(process_job, vimeo_url, activity_id)
    return jsonify({"job_id": job.get_id(), "status": "queued"})

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
    app.run(host="0.0.0.0", port=5000)

