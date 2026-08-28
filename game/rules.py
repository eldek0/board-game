from dataclasses import replace
from game.board import END
from game.state import Player, GameState


def move_player(player: Player, steps: int) -> Player:
    new_position = min(player.position + steps, END)

    return replace(
        player,
        position=new_position
    )

def play_turn(game_state: GameState, dice_num: int)->GameState:
    if dice_num not in range(1, 7):
        raise ValueError("Dice number must be between 1 and 6")

    # Some action
    player_index = game_state.turn % len(game_state.players)
    player = game_state.players[player_index]
    new_player = move_player(player=player, steps=dice_num)
    players_list = tuple(
        new_player if i == player_index else p
        for i, p in enumerate(game_state.players)
    )

    return replace(
        game_state,
        players=players_list,
        winner=new_player if is_winner(new_player) else None,
        turn=game_state.turn+1
    )

def is_winner(player: Player) -> bool:
    return player.position >= END