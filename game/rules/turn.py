from dataclasses import replace
from game.log import log
from game.state import Player, GameState
from game.rules.movement import move_player, is_winner
from game.rules.landing import resolve_landing
from game.rules.competition import find_rival, start_fight


def play_turn(game_state: GameState, dice_num: int)->GameState:
    """Plays one full turn, unless it runs into a competition.

    Landing on an occupied cell suspends the turn instead of finishing it: the
    state comes back with a pending fight and the turn counter untouched, and
    roll_fight carries it the rest of the way once both dice are in.
    """
    if dice_num not in range(1, 7):
        raise ValueError("Dice number must be between 1 and 6")

    if game_state.fight is not None:
        raise ValueError("Hay una competencia pendiente: usar roll_fight")

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

    players_list = _place_player(other_players, player_index, moved_player)
    moved_state = replace(game_state, players=players_list)

    rival_index = find_rival(players_list, player_index)
    if rival_index is not None:
        return start_fight(moved_state, player_index, rival_index)

    return end_turn(moved_state, player_index)


def end_turn(game_state: GameState, player_index: int) -> GameState:
    """Closes the turn: crowns the mover if it reached FIN and hands over the dice.

    Shared by the plain path and by the one that had to stop for a competition, so
    a turn is counted exactly once either way.
    """
    player = game_state.players[player_index]
    winner = player if is_winner(player) else None

    if winner:
        log(f"¡{winner.name} llegó al FIN y ganó la partida!")

    return replace(
        game_state,
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
