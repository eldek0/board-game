import random
from game.board import START, END
from game.log import log
from game.state import Player
from game.rules.occupancy import players_at_position, move_back_until_free

def resolve_competition(
    player: Player,
    other_players: tuple[Player, ...],
    rng: random.Random
) -> tuple[Player, tuple[Player, ...]]:
    """If player lands on a cell held by a rival, both roll and the loser
    retreats (further, if that retreat lands on yet another occupied cell).
    START and END are exempt so the game can't stall there.
    """
    if player.position in (START, END):
        return player, other_players

    rivals = players_at_position(other_players, player.position, player.color)
    if not rivals:
        return player, other_players

    rival = rivals[0]
    player_roll = rng.randint(1, 6)
    rival_roll = rng.randint(1, 6)

    if player_roll == rival_roll:
        return resolve_competition(player, other_players, rng)

    if player_roll > rival_roll:
        log(f"{player.name} won the tie-breaker against {rival.name} ({player_roll} vs {rival_roll})")
        moved_rival = move_back_until_free(rival, other_players)
        new_others = tuple(
            moved_rival if p is rival else p for p in other_players
        )
        return player, new_others

    log(f"{player.name} lost the tie-breaker against {rival.name} ({player_roll} vs {rival_roll})")
    moved_player = move_back_until_free(player, other_players)
    return moved_player, other_players
