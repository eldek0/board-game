import argparse
import random

from game.state import Player, GameState
from game.rules import *
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

    print(f"Game Info: SEED={seed}, PLAYERS={player_amount}")

    return GameState(
        players=tuple(
            Player(name=f"Player {i+1}", color=colors[i]) 
            for i in range(0, player_amount)
        ),
        rng=rng
    )

def game_recursion(game_state:GameState):
    if game_state.winner:
        print(f"The winner is {game_state.winner.name} color={game_state.winner.color}")
        return

    roll_dice = game_state.rng.randint(1, 6)
    new_state = play_turn(game_state, roll_dice)

    game_recursion(new_state)

if __name__ == "__main__":
    game_state = initialize()

    game_recursion(game_state)
