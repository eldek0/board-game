ROWS = 9
COLS = 10

# Recorrido del tablero empezando en INICIO
LEFT = tuple((row, 0) for row in range(ROWS - 1, -1, -1))

TOP = tuple((0, col) for col in range(1, COLS))

RIGHT = tuple((row, COLS - 1) for row in range(1, ROWS))

BOTTOM = tuple(
    (ROWS - 1, col)
    for col in range(COLS - 2, 0, -1)
)

PATH = LEFT + TOP + RIGHT + BOTTOM

INICIO = 0
FIN = len(PATH) - 1

SPECIAL = {
    4: "P1",
    10: "P2",
    15: "C1",
    21: "P3",
    27: "C2",
}


def coord(posicion):
    return PATH[posicion]


def tipo_casilla(posicion):
    if posicion == INICIO:
        return "INICIO"

    if posicion == FIN:
        return "FIN"

    return SPECIAL.get(posicion, "NORMAL")