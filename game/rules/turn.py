from dataclasses import replace
from game.log import log
from game.state import Player, GameState
from game.rules.movement import move_player, is_winner
from game.rules.landing import resolve_landing
from game.rules.competition import resolve_competition


def play_turn(game_state: GameState, dice_num: int)->GameState:
    if dice_num not in range(1, 7):
        raise ValueError("Dice number must be between 1 and 6")

    player_index = game_state.turn % len(game_state.players)
    player = game_state.players[player_index]
    other_players = tuple(
        p for i, p in enumerate(game_state.players) if i != player_index
    )
    log(f"-Turno #{game_state.turn+1}-")

    # A punished player burns one skip instead of rolling
    if player.turns_to_skip > 0:
        log(f"{player.name} pierde este turno (castigos pendientes: {player.turns_to_skip})")
        skipped_player = replace(player, turns_to_skip=player.turns_to_skip - 1)
        players_list = _place_player(other_players, player_index, skipped_player)
        return replace(game_state, players=players_list, turn=game_state.turn+1)

    log(f"{player.name} tiró el dado y sacó un {dice_num}")
    moved_player = move_player(player=player, steps=dice_num)
    log(f"{player.name} avanzó {dice_num} casillas")

    moved_player, other_players = resolve_landing(moved_player, other_players, game_state.rng)
    moved_player, other_players = resolve_competition(moved_player, other_players, game_state.rng)

    players_list = _place_player(other_players, player_index, moved_player)
    winner = moved_player if is_winner(moved_player) else None

    if winner:
        log(f"¡{winner.name} llegó al FIN y ganó la partida!")

    return replace(
        game_state,
        players=players_list,
        winner=winner,
        turn=game_state.turn+1
    )


def _place_player(
    other_players: tuple[Player, ...],
    index: int,
    player: Player
) -> tuple[Player, ...]:
    """Rebuilds the full players tuple, putting player back at its original index."""
    players = list(other_players)
    players.insert(index, player)
    return tuple(players)
