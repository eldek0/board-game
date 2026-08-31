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
class Fight:
    """A competition that is waiting on its dice.

    Both players roll before the cell is decided, and in interactive mode each
    roll is a separate key press, so the turn has to survive between them. Players
    are held by index into GameState.players, never as copies, so the tuple stays
    the single source of truth for where everyone is.
    """
    challenger: int
    rival: int
    challenger_roll: int | None = None
    rival_roll: int | None = None


@dataclass(frozen=True)
class GameState:
    players: tuple[Player, ...]
    rng: random.Random
    winner: Player | None = None
    turn: int = 0
    # Set while a competition is unresolved; the turn counter holds until it clears
    fight: Fight | None = None



