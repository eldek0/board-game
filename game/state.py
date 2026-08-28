from dataclasses import dataclass
from game.board import INICIO

@dataclass(frozen=True)
class Player:
    name: str
    color: tuple[int, int, int]
    position: int = INICIO
    turns_to_skip: int = 0


@dataclass(frozen=True)
class GameState:
    players: tuple[Player, ...]
    winner: str | None = None



