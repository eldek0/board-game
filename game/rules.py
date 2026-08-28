from dataclasses import replace
from game.board import FIN
from game.state import Player


def move_player(player: Player, steps: int) -> Player:
    new_position = min(player.position + steps, FIN)

    return replace(
        player,
        position=new_position
    )


def is_winner(player: Player) -> bool:
    return player.position >= FIN