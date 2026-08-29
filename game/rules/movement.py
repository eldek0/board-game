from dataclasses import replace
from game.board import END, START
from game.state import Player


def move_player(player: Player, steps: int) -> Player:
    new_position = min(player.position + steps, END)

    return replace(
        player,
        position=new_position
    )

def move_back(player: Player, steps: int) -> Player:
    new_position = max(player.position - steps, START)

    return replace(
        player,
        position=new_position
    )

def is_winner(player: Player) -> bool:
    return player.position >= END
