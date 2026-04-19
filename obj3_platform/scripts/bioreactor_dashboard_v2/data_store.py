import sqlite3, time
from collections import deque

HISTORY = 300   # keep last 300 readings
_buffer: deque = deque(maxlen=HISTORY)

def push_reading(d: dict):
    d["ts"] = time.time()
    _buffer.append(d)

def latest() -> dict:
    return _buffer[-1] if _buffer else {}

def history() -> list:
    return list(_buffer)