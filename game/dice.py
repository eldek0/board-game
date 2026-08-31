import random
from collections.abc import Iterator


def dice_stream(rng: random.Random) -> Iterator[int]:
    #genera indefinidamente valores de dado entre 1 y 6.
    while True:
        yield rng.randint(1, 6)