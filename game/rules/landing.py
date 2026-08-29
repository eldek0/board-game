import random
from game.board import SPECIAL
from game.state import Player
from game.rules.movement import is_winner
from game.rules.effects import apply_p1, apply_p2, apply_p3, apply_c1, apply_c2

# Depth cap so a P2/P3/C2 chain landing on itself over and over can't recurse forever
MAX_LANDING_DEPTH = 10

def resolve_landing(
    player: Player,
    other_players: tuple[Player, ...],
    rng: random.Random,
    depth: int = 0
) -> tuple[Player, tuple[Player, ...]]:
    """Applies the effect of the cell the player just landed on, if any."""
    if depth >= MAX_LANDING_DEPTH or is_winner(player):
        return player, other_players

    cell = SPECIAL.get(player.position)

    if cell == "P1":
        target = max(other_players, key=lambda p: p.position, default=None)
        if target is None:
            return player, other_players
        print(f"{player.name} landed on P1: {target.name} loses a turn")
        punished_target = apply_p1(target)
        new_others = tuple(
            punished_target if p is target else p for p in other_players
        )
        return player, new_others

    if cell == "P2":
        extra_roll = rng.randint(1, 6)
        print(f"{player.name} landed on P2: rolled a {extra_roll} again")
        moved_player = apply_p2(player, extra_roll)
        return resolve_landing(moved_player, other_players, rng, depth + 1)

    if cell == "P3":
        print(f"{player.name} landed on P3: advances 2 cells")
        moved_player = apply_p3(player)
        return resolve_landing(moved_player, other_players, rng, depth + 1)

    if cell == "C1":
        print(f"{player.name} landed on C1: loses next turn")
        return apply_c1(player), other_players

    if cell == "C2":
        print(f"{player.name} landed on C2: goes back 3 cells")
        moved_player = apply_c2(player)
        return resolve_landing(moved_player, other_players, rng, depth + 1)

    return player, other_players
