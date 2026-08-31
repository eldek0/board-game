from dataclasses import replace
from game.state import Player
from game.rules.movement import move_player, move_back


def apply_p3(player: Player) -> Player:
    return move_player(player, 2)

def apply_c2(player:Player) -> Player:
    return move_back(player, 3)


def lose_turn(player: Player) -> Player:
    return replace(
        player,
        turns_to_skip=player.turns_to_skip + 1
    )

def apply_c1(player: Player) -> Player:
    return lose_turn(player)

def apply_p1(target_player: Player) -> Player:
    return lose_turn(target_player)

def apply_p2(player: Player, extra_roll: int) -> Player:
    return move_player(player, extra_roll)
