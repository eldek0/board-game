import random
from dataclasses import dataclass
from game.board import START

@dataclass(frozen=True)
class Player:
    name: str
    color: tuple[int, int, int]
    position: int = START
    turns_to_skip: int = 0


@dataclass(frozen=True)
class GameState:
    players: tuple[Player, ...]
    rng: random.Random
    winner: Player | None = None
    turn: int = 0



