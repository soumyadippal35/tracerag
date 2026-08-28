import logging
import os
import time
from collections import defaultdict, deque
from pathlib import Path

logger = logging.getLogger("tracerag")


class RateLimiter:
    def __init__(self, limit: int = 120, window_seconds: int = 60):
        self.limit = limit
        self.window_seconds = window_seconds
        self.events: dict[str, deque[float]] = defaultdict(deque)
        self.redis = None
        if os.getenv("TRAGERAG_REDIS_URL"):
            import redis
            self.redis = redis.from_url(os.environ["TRAGERAG_REDIS_URL"], decode_responses=True)

    def allowed(self, key: str) -> bool:
        if self.redis:
            bucket = f"tracerag:rate:{key}:{int(time.time() // self.window_seconds)}"
            count = self.redis.incr(bucket)
            if count == 1:
                self.redis.expire(bucket, self.window_seconds)
            return count <= self.limit
        now = time.time()
        events = self.events[key]
        while events and events[0] <= now - self.window_seconds:
            events.popleft()
        if len(events) >= self.limit:
            return False
        events.append(now)
        return True


class BlobStore:
    def __init__(self) -> None:
        self.bucket = os.getenv("TRAGERAG_S3_BUCKET")
        self.prefix = os.getenv("TRAGERAG_S3_PREFIX", "documents").strip("/")
        self.local_dir = Path(os.getenv("TRAGERAG_UPLOAD_DIR", "data/uploads"))
        self.local_dir.mkdir(parents=True, exist_ok=True)
        self.client = None
        if self.bucket:
            import boto3
            self.client = boto3.client("s3", endpoint_url=os.getenv("TRAGERAG_S3_ENDPOINT"))

    def put(self, name: str, content: bytes) -> None:
        if self.client:
            self.client.put_object(Bucket=self.bucket, Key=f"{self.prefix}/{name}", Body=content)
        else:
            (self.local_dir / Path(name).name).write_bytes(content)
