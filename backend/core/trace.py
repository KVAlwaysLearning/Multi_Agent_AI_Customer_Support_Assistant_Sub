"""
This is the verification tool for the whole architecture.

Every request through /chat builds up a Trace object as it passes through
each component (intent -> router -> agent(s) -> retrieval -> aggregator).
The trace is returned in the API response AND logged, so you can see -
without reading code - that input actually flowed through every required
stage and called the right function, before any real feature logic exists.
"""
import time
import logging
import json

logger = logging.getLogger("trace")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")


class Trace:
    def __init__(self, session_id: str, message: str):
        self.session_id = session_id
        self.message = message
        self.steps = []
        self._start = time.time()

    def log(self, stage: str, detail: dict):
        elapsed_ms = round((time.time() - self._start) * 1000, 2)
        entry = {"stage": stage, "elapsed_ms": elapsed_ms, "detail": detail}
        self.steps.append(entry)
        logger.info(f"[TRACE] session={self.session_id} stage={stage} detail={json.dumps(detail)}")

    def as_dict(self):
        return {
            "session_id": self.session_id,
            "message": self.message,
            "steps": self.steps,
            "total_elapsed_ms": round((time.time() - self._start) * 1000, 2),
        }
