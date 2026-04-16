import redis
import json
r = redis.Redis()

class ProgressStore:
    @staticmethod
    def set(job_id, data):
        r.set(f"progress:{job_id}", json.dumps(data))

    @staticmethod
    def get(job_id):
        data = r.get(f"progress:{job_id}")
        return json.loads(data) if data else {}