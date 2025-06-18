import time
import threading
from collections import defaultdict

class UsageTracker:
    def __init__(self):
        self.usage = defaultdict(lambda: {"count": 0, "last_reset": time.time()})
        self.locks = defaultdict(threading.Lock)
        self.limits = defaultdict(lambda: 1000)  # Default: 1000 calls per hour per model

    def set_limit(self, model_id, limit):
        self.limits[model_id] = limit

    def increment(self, model_id):
        with self.locks[model_id]:
            now = time.time()
            if now - self.usage[model_id]["last_reset"] > 3600:
                self.usage[model_id]["count"] = 0
                self.usage[model_id]["last_reset"] = now
            self.usage[model_id]["count"] += 1
            return self.usage[model_id]["count"]

    def is_limited(self, model_id):
        with self.locks[model_id]:
            now = time.time()
            if now - self.usage[model_id]["last_reset"] > 3600:
                self.usage[model_id]["count"] = 0
                self.usage[model_id]["last_reset"] = now
            return self.usage[model_id]["count"] >= self.limits[model_id]

    def get_usage(self, model_id):
        return self.usage[model_id]["count"]
