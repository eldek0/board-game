import argparse
import random

from game.state import Player, GameState
from game.rules import *
from game.dice import dice_stream
from files.utils import player_colors

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=random.randint(0, 9999))
    parser.add_argument("--players", type=int, default=3)
    return parser.parse_args()

def initialize()->GameState:
    args = get_args()
    player_amount:int = args.players
    seed:int = args.seed
    rng = random.Random(seed) # With the seed

    # Unique color
    colors = player_colors(player_amount, seed)

    print(f"Semilla: {seed} - Jugadores: {player_amount}")

    return GameState(
        players=tuple(
            Player(name=f"Player {i+1}", color=colors[i]) 
            for i in range(0, player_amount)
        ),
        rng=rng
    )


def game_recursion(game_state: GameState, dice_generator):
    if game_state.winner:
        print(
            f"Ganó {game_state.winner.name} "
            f"color={game_state.winner.color}"
        )
        return

    roll_dice = next(dice_generator)

    new_state = play_turn(
        game_state,
        roll_dice
    )

    game_recursion(
        new_state,
        dice_generator
    )

if __name__ == "__main__":
    game_state = initialize()

    dice_generator = dice_stream(game_state.rng)

    game_recursion(
        game_state, 
        dice_generator
    )
