from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from threading import Lock
from uuid import uuid4


@dataclass
class SessionRecord:
    session_id: str
    created_at: datetime
    last_activity_at: datetime
    history: list[dict[str, str]] = field(default_factory=list)
    status: str = "active"
    question_count: int = 0


class SessionNotFoundError(Exception):
    pass


class SessionExpiredError(Exception):
    pass


class SessionStore:
    def __init__(self, ttl_minutes: int = 30) -> None:
        self._ttl = timedelta(minutes=ttl_minutes)
        self._sessions: dict[str, SessionRecord] = {}
        self._lock = Lock()

    def _now(self) -> datetime:
        return datetime.now(UTC)

    def _is_expired(self, record: SessionRecord) -> bool:
        return self._now() - record.last_activity_at > self._ttl

    def cleanup_expired(self) -> None:
        with self._lock:
            for session_id, record in list(self._sessions.items()):
                if self._is_expired(record):
                    record.status = "expired"
                    del self._sessions[session_id]

    def create_session(self) -> SessionRecord:
        now = self._now()
        record = SessionRecord(session_id=str(uuid4()), created_at=now, last_activity_at=now)
        with self._lock:
            self._sessions[record.session_id] = record
        return record

    def get_session(self, session_id: str) -> SessionRecord:
        with self._lock:
            record = self._sessions.get(session_id)
            if record is None:
                raise SessionNotFoundError(session_id)
            if self._is_expired(record):
                record.status = "expired"
                del self._sessions[session_id]
                raise SessionExpiredError(session_id)
            return record

    def touch(self, session_id: str) -> SessionRecord:
        record = self.get_session(session_id)
        with self._lock:
            record.last_activity_at = self._now()
        return record

    def append_turn(self, session_id: str, role: str, content: str) -> SessionRecord:
        record = self.touch(session_id)
        with self._lock:
            record.history.append({"role": role, "content": content})
            if role == "user":
                record.question_count += 1
            record.last_activity_at = self._now()
        return record

    def reset_session(self, session_id: str) -> None:
        with self._lock:
            if session_id not in self._sessions:
                raise SessionNotFoundError(session_id)
            self._sessions[session_id].status = "reset"
            del self._sessions[session_id]

    def expires_in_seconds(self) -> int:
        return int(self._ttl.total_seconds())
