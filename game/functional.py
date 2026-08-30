from collections.abc import Callable
from typing import TypeVar


A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")


def compose(
    f: Callable[[B], C],
    g: Callable[[A], B]
) -> Callable[[A], C]:
   #compone dos funciones: compose(f, g)(x) = f(g(x)).
    return lambda x: f(g(x))


normalize_name = compose(
    str.casefold,
    str.strip           ##aca esta la composicion de funciones, 
                        ##primero hace strip y despues casefold
)