import time
import logging
from collections import defaultdict

class Telemetry:
    def __init__(self):
        self.metrics = defaultdict(list)

    def log(self, event, value):
        self.metrics[event].append((time.time(), value))
        logging.info(f"[Telemetry] {event}: {value}")

    def get_metrics(self, event=None):
        if event:
            return self.metrics[event]
        return dict(self.metrics)
