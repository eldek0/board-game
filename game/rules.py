from dataclasses import replace
from game.board import END, START
from game.state import Player, GameState


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

def play_turn(game_state: GameState, dice_num: int)->GameState:
    if dice_num not in range(1, 7):
        raise ValueError("Dice number must be between 1 and 6")

    # Some action
    player_index = game_state.turn % len(game_state.players)
    player = game_state.players[player_index]
    print(f"Turn #{game_state.turn+1} - {player.name}'s turn")
    print(f"{player.name} throwed the dice and got a {dice_num}")

    new_player = move_player(player=player, steps=dice_num)
    players_list = tuple(
        new_player if i == player_index else p
        for i, p in enumerate(game_state.players)
    )
    print(f"{player.name} advanced {dice_num} cells")

    input()

    return replace(
        game_state,
        players=players_list,
        winner=new_player if is_winner(new_player) else None,
        turn=game_state.turn+1
    )

def is_winner(player: Player) -> bool:
    return player.position >= END


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

    if is_position_occupied(
        moved_player.position, 
        players, 
        player.color
    ):
        return move_back_until_free(
            moved_player, 
            players, 
            steps)
    return moved_player