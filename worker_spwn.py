import multiprocessing
#multiprocessing.set_start_method('spawn', force=True)
multiprocessing.set_start_method("fork", force=True)  # ✅ FIXES macOS subprocess issue
import os
import redis
from rq import Worker, Queue  # Correct import

# Queues to listen to
listen = ['default']  # This is a list of queue names

# Redis connection
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
conn = redis.from_url(redis_url)

if __name__ == '__main__':
    # Create and start the worker with the correct parameters
    worker = Worker(queues=listen, connection=conn)
    worker.work()