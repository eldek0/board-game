from game.board import START
from game.state import Player
from game.rules.movement import move_back


def players_at_position(
    players: tuple[Player, ...],
    position: int,
    excluded_color: tuple[int, int, int] | None = None
) -> tuple[Player, ...]:
    return tuple(
        filter(
            lambda player:
                player.position == position and
                player.color != excluded_color, players
        )
    )

def is_position_occupied(
    position: int,
    players: tuple[Player, ...],
    excluded_color: tuple[int, int, int] | None = None
) -> bool:
    return len(
        players_at_position(players, position, excluded_color)
    ) > 0


def move_back_until_free(
    player: Player,
    players: tuple[Player, ...],
    steps: int = 2
) -> Player:
    moved_player = move_back(player, steps)

    # START is an exception
    if moved_player.position != START and is_position_occupied(
        moved_player.position,
        players,
        player.color
    ):
        return move_back_until_free(
            moved_player,
            players,
            steps)
    return moved_player
