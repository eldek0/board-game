from dataclasses import replace
from game.board import START, END
from game.log import log
from game.state import Fight, GameState, Player
from game.rules.occupancy import move_back_until_free


def find_rival(players: tuple[Player, ...], challenger_index: int) -> int | None:
    """Index of a rival sharing the challenger's cell, or None if nobody contests it.

    START and END are exempt so the game can neither stall at the entrance nor
    rob a player of a win on the last cell.
    """
    challenger = players[challenger_index]

    if challenger.position in (START, END):
        return None

    return next(
        (
            index
            for index, player in enumerate(players)
            if index != challenger_index
            and player.position == challenger.position
            and player.color != challenger.color
        ),
        None
    )


def start_fight(game_state: GameState, challenger_index: int, rival_index: int) -> GameState:
    """Suspends the turn on a pending competition, waiting for both dice."""
    challenger = game_state.players[challenger_index]
    rival = game_state.players[rival_index]

    log(f"{challenger.name} cayó en la casilla de {rival.name}: compiten por el casillero")

    return replace(
        game_state,
        fight=Fight(challenger=challenger_index, rival=rival_index)
    )


def is_fight_rolled(game_state: GameState) -> bool:
    """True once both dice are on the table and only the verdict is left."""
    fight = game_state.fight
    return fight is not None and fight.rival_roll is not None


def pending_roller(game_state: GameState) -> Player | None:
    """The player who still owes a roll, or None if both have already rolled."""
    fight = game_state.fight

    if fight is None or is_fight_rolled(game_state):
        return None

    if fight.challenger_roll is None:
        return game_state.players[fight.challenger]

    return game_state.players[fight.rival]


def fight_winner(game_state: GameState) -> Player | None:
    """Who takes the cell, or None on a tie or while a die is still missing."""
    fight = game_state.fight

    if not is_fight_rolled(game_state) or fight.challenger_roll == fight.rival_roll:
        return None

    return game_state.players[
        fight.challenger if fight.challenger_roll > fight.rival_roll else fight.rival
    ]


def fight_outcome(game_state: GameState) -> str | None:
    """One line naming the verdict, for the board to show before it is applied."""
    fight = game_state.fight

    if not is_fight_rolled(game_state):
        return None

    score = f"{fight.challenger_roll} vs {fight.rival_roll}"
    winner = fight_winner(game_state)

    if winner is None:
        return f"Empate en {fight.challenger_roll}: vuelven a tirar"

    return f"Gana {winner.name} ({score})"


def roll_fight(game_state: GameState, dice_num: int) -> GameState:
    """Records one competition die, and nothing else.

    Deliberately stops at the second roll instead of resolving: both faces have to
    stay on screen long enough to be read, so applying the outcome is a separate
    step driven by resolve_fight.
    """
    if dice_num not in range(1, 7):
        raise ValueError("Dice number must be between 1 and 6")

    fight = game_state.fight

    if fight is None:
        raise ValueError("No hay una competencia pendiente")

    if is_fight_rolled(game_state):
        raise ValueError("Ambos jugadores ya tiraron: usar resolve_fight")

    roller = pending_roller(game_state)
    log(f"{roller.name} tiró un {dice_num} en la competencia")

    if fight.challenger_roll is None:
        return replace(game_state, fight=replace(fight, challenger_roll=dice_num))

    return replace(game_state, fight=replace(fight, rival_roll=dice_num))


def resolve_fight(game_state: GameState) -> GameState:
    """Applies the verdict of a fully rolled competition.

    A tie clears both dice and the pair rolls again; otherwise the loser retreats
    and the suspended turn is finally closed.
    """
    from game.rules.turn import end_turn

    if not is_fight_rolled(game_state):
        raise ValueError("La competencia todavía no tiene los dos dados")

    fight = game_state.fight
    challenger = game_state.players[fight.challenger]
    rival = game_state.players[fight.rival]
    winner = fight_winner(game_state)

    if winner is None:
        log(f"Empate en {fight.challenger_roll}: {challenger.name} y {rival.name} vuelven a tirar")
        return replace(
            game_state,
            fight=replace(fight, challenger_roll=None, rival_roll=None)
        )

    challenger_wins = winner is challenger
    loser = rival if challenger_wins else challenger
    loser_index = fight.rival if challenger_wins else fight.challenger

    log(
        f"{winner.name} ganó la competencia contra {loser.name} "
        f"({fight.challenger_roll} vs {fight.rival_roll})"
    )

    others = tuple(
        player for index, player in enumerate(game_state.players)
        if index != loser_index
    )
    moved_loser = move_back_until_free(loser, others)
    log(f"{loser.name} retrocede a la casilla {moved_loser.position}")

    players = tuple(
        moved_loser if index == loser_index else player
        for index, player in enumerate(game_state.players)
    )

    return end_turn(
        replace(game_state, players=players, fight=None),
        fight.challenger
    )
