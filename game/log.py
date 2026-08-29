"""Game event log: only player-facing turn messages, for the on-screen console box."""
from collections import deque

_lines: deque[str] = deque(maxlen=500)
_unread: list[str] = []

def log(message: str) -> None:
	"""Records a player-facing game event and echoes it to the terminal."""
	msg = message
	_lines.append(msg)
	_unread.append(msg)

def lines() -> list[str]:
	"""Every recorded line, oldest first."""
	return list(_lines)

def drain() -> list[str]:
	"""The lines recorded since the previous drain."""
	global _unread
	out = _unread
	_unread = []
	return out

def clear() -> None:
	_lines.clear()
	_unread.clear()
