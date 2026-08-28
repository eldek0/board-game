# board-game

Entregable 1 — Programación Avanzada (UM, Curso 2026)
Juego de tablero implementado con el paradigma de **programación funcional** en Python.

## Install dependencies

    pip install -r requirements.txt

## Ejecutar

    python main.py                                   # juego con interfaz gráfica
    python -m game.simulate --seed 42 --players 3    # simulación headless (sin ventana)

---

# Plan de implementación

> Hoja de ruta acordada antes de repartir el trabajo. Todavía **no hay código de juego escrito**:
> el repo tiene únicamente el scaffold de pygame-ce (`files/`).

## 1. Resumen de la letra

- **Entrega:** 01/09 12:00 por Moodle. Presentación en clase 31/08 – 01/09, los integrantes presentes.
- Juego de tablero para **2-4 jugadores** de distinto color, con interfaz gráfica. Gana quien llega
  primero al FIN.
- **Grupo de 3 personas → aplica el Anexo II:** cada jugador tiene **4 fichas** (estilo ludo) y gana
  cuando las 4 llegan al FIN. No hay restricción sobre cuántas fichas pueden estar jugando a la vez.

### Modos (se eligen al arrancar)

| Modo | Comportamiento |
|---|---|
| **Simulación** | Se juega solo, de punta a punta, con una pausa visible en cada turno. |
| **Interactivo** | Pide los nombres de los jugadores; en cada turno el usuario presiona una tecla para tirar el dado y se muestra el valor, la casilla que tocó, el premio/castigo y cómo queda el tablero. |

### Reglas

1. Todos arrancan en **INICIO** y avanzan con un dado 1-6. No hace falta ningún valor especial para
   empezar a moverse.
2. El juego termina cuando un jugador alcanza **FIN**.
3. Al caer en una casilla de premio (P1, P2, P3) o castigo (C1, C2) se ejecuta su acción.
4. **Competencia:** si un jugador cae en la casilla de otro, tiran ambos el dado; el mayor se queda
   en la casilla y el perdedor **retrocede 2**. Si el perdedor vuelve a caer en una casilla ocupada,
   **retrocede 1 más**.
5. **No hay rebote:** si faltan 5 para el FIN y sale 6, igual se termina.

### Premios y castigos

| Casilla | Efecto |
|---|---|
| **P1** | Elige un color para que pierda un turno |
| **P2** | Tira el dado nuevamente y avanza |
| **P3** | Avanza 2 casillas |
| **C1** | Pierde 1 turno |
| **C2** | Retrocede 3 casillas |

### Requisitos funcionales obligatorios (mínimo)

funciones puras · composición de funciones · comprensiones · generador (`yield`) ·
`map`/`filter`/`reduce` · recursión · un decorador para hacer log

### Forma de entrega

Zip `Entregable1<Apellido1><Apellido2><Apellido3>.zip` con:
1. Código fuente.
2. Informe técnico en PDF: (a) decisiones tomadas, (b) dónde se aplicó cada herramienta funcional,
   (c) análisis de dónde fue posible mantener inmutabilidad y pureza y dónde no, (d) cómo ejecutarlo,
   (e) conclusiones.

## 2. Modelo del tablero (Anexo I)

La grilla del anexo es de **10 columnas × 9 filas**; las celdas grises del centro son interior no
transitable. El camino es el **anillo perimetral**:

    2 × 10 + 2 × 9 − 4 = 34 casillas

Se recorre en sentido antihorario desde INICIO (abajo-izquierda): sube por la columna izquierda,
cruza la fila superior, baja por la columna derecha y vuelve por la fila inferior hacia la izquierda.
**FIN queda pegado a INICIO**, en el índice 33.

Índices derivados y verificados contra el anexo:

| Índice | Casilla | Coord (fila, col) |
|---|---|---|
| 0 | INICIO | (8, 0) |
| 4 | **P1** — elige un color que pierda un turno | (4, 0) |
| 10 | **P2** — tira de nuevo y avanza | (0, 2) |
| 15 | **C1** — pierde 1 turno | (0, 7) |
| 21 | **P3** — avanza 2 casillas | (4, 9) |
| 27 | **C2** — retrocede 3 casillas | (8, 7) |
| 33 | FIN | (8, 1) |

## 3. Arquitectura: *functional core / imperative shell*

Toda la lógica del juego vive en un paquete **`game/` puro**: sin pygame, sin I/O y sin azar
generado adentro. Pygame queda como cáscara que solo dibuja el estado y empuja eventos hacia el core.

No es una decisión de estilo. Es lo que permite:
- responder con evidencia el punto (c) del informe (qué quedó puro y qué no),
- testear el juego completo sin abrir una ventana,
- que una misma semilla produzca siempre la misma partida.

### Módulos del core

| Módulo | Contenido |
|---|---|
| `game/board.py` | `PATH` (comprensión encadenando los 4 tramos), `SPECIAL` (comprensión de diccionario), `coord()`, `cell_kind()`, `INICIO`, `FIN` |
| `game/state.py` | `Piece` / `Player` / `GameState` como `NamedTuple` inmutables; `occupants()` con `filter`; `advance()` con tope en FIN (regla 5) |
| `game/rules.py` | `play_turn(state, dice) -> GameState` y los resolvers puros; `resolve_landing` y `resolve_competition` **recursivos** |
| `game/dice.py` | `dice_stream(seed)` y `turn_cycle(n)` con **`yield`**; el azar queda sembrado y aislado en un solo lugar |
| `game/functional.py` | `compose` / `pipe` y el decorador **`@log_call`** |
| `game/simulate.py` | `game_history()` (generador de estados turno a turno) y `run()` con **`reduce`**; corre headless |

### Forma del estado

```python
class Piece(NamedTuple):   idx: int; pos: int; finished: bool
class Player(NamedTuple):  name: str; color: tuple; pieces: tuple[Piece, ...]; skips: int
class GameState(NamedTuple):
    players: tuple[Player, ...]
    turn: int                    # índice del jugador al que le toca
    rolls: tuple[int, ...]       # dados consumidos este turno (para la vista)
    log: tuple[str, ...]         # historial textual
    winner: int | None
```

Todo se "modifica" con `._replace`, nunca in-place.

## 4. Reglas ambiguas — ya decididas

La letra deja estos casos abiertos. Se fijan acá para que los tres integrantes programen lo mismo, y
van documentados en el informe:

1. **INICIO y FIN están exentos de competencia.** Es necesario: con 4 fichas, todas arrancan
   apiladas en INICIO.
2. **Fichas del mismo color apilan sin competir** (el Anexo II lo dice explícitamente).
3. **La ficha entrante compite una vez contra la pila rival como unidad.** Si pierde la pila,
   retrocede entera 2 casillas.
4. **Los efectos de casilla se re-evalúan** cuando P3 o C2 reubican una ficha, con un tope de
   profundidad para cortar ciclos patológicos.
5. **Empate en competencia:** se vuelve a tirar (llamada recursiva).
6. **P1:** en simulación elige por heurística determinista (el rival más adelantado); en interactivo
   lo elige el usuario.
7. **C2 no puede dejar una ficha por debajo de INICIO** (se topea en 0).

## 5. Capa gráfica — qué se reusa del scaffold

| Archivo | Qué se hace |
|---|---|
| `files/app_main.py` | Se le agrega la máquina de escenas: menú → setup → juego → ganador. El loop, `get_deltatime` y `mouse_control` quedan **como están**. |
| `files/draw.py` | Hoy es un stub de una línea. Pasa a dibujar el tablero desde el `GameState`: celdas con `map` sobre `PATH`, fichas con `pygame.draw.circle`, panel lateral con turno / dado / últimas líneas de log. |
| `files/animation.py` | **Se reusa tal cual** para la pausa entre turnos del modo simulación: `new_animation("turn_pause", 0, 0.8)` y disparar el turno cuando incrementa `get_times_limit_reached`. No se escribe ningún timer nuevo. |
| `files/utils.py` | `text()` ya cubre todo el HUD. |
| `files/import_imp.py` | Solo fuentes. **No hacen falta sprites nuevos**: las fichas se dibujan con primitivas. |
| `files/text_input.py` | **Nuevo.** Mini widget de entrada de texto (`KEYDOWN` + `event.unicode` + backspace) para pedir los nombres dentro de la ventana, como pide la letra. |

**Controles:** `ESPACIO` tira el dado · `1-4` elige ficha (Anexo II) o color rival al caer en P1 ·
`ESC` vuelve al menú.

## 6. Mapa requisito funcional → dónde se cumple

Esta tabla es la base del punto (b) del informe.

| # | Requisito | Dónde |
|---|---|---|
| 1 | Funciones puras | todo `game/rules.py`, `game/board.py`, `game/state.py` |
| 2 | Composición de funciones | `compose` / `pipe` en `game/functional.py`, encadenando los resolvers de efectos en `rules.py` |
| 3 | Comprensiones | `PATH` (tupla) y `SPECIAL` (dict) en `board.py`; rects del render en `draw.py` |
| 4 | Generador (`yield`) | `dice_stream`, `turn_cycle` en `dice.py`; `game_history` en `simulate.py` |
| 5 | `map` / `filter` / `reduce` | `reduce` en `simulate.run`, `filter` en `occupants`, `map` en el render |
| 6 | Recursión | `resolve_competition` (cadena de retrocesos), `resolve_landing` (re-tiro de P2) |
| 7 | Decorador de log | `@log_call` en `functional.py`, aplicado a las transiciones de `rules.py` |

## 7. Orden de trabajo

1. `game/board.py` + `game/state.py` — la base inmutable.
2. `game/dice.py` + `game/functional.py` — generador y decorador, se necesitan enseguida.
3. `game/rules.py` — el grueso; incluye el Anexo II (4 fichas y elección de ficha).
4. `game/simulate.py` + verificación headless.
5. Escenas y render en pygame.
6. `files/text_input.py` y modo interactivo.
7. Informe + zip.

Los pasos 1-4 no dependen de pygame, así que se pueden hacer en paralelo con el 5.

## 8. Entregables no-código

- `informe.md` → exportado a PDF, con las secciones (a)-(e) exactas que pide la letra.
- Zip `Entregable1<Apellido1><Apellido2><Apellido3>.zip`, excluyendo `venv/` y `__pycache__/`
  (ya están en `.gitignore`). **Pendiente: los tres apellidos.**

## 9. Verificación

- `python -m game.simulate --seed 42 --players 3` corrido con ~200 semillas: **ninguna partida debe
  colgarse**. El riesgo real está en la recursión de competencia y en el re-tiro encadenado de P2.
- **Determinismo:** la misma semilla produce el mismo log carácter a carácter (prueba de pureza del core).
- **Inmutabilidad:** el estado previo queda intacto después de `play_turn`.
- Casos de borde en pytest: sin rebote (faltan 5, sale 6 → gana), retroceso encadenado por
  competencia, C2 desde posición baja, P2 encadenado, victoria del Anexo II solo con las 4 fichas en FIN.
- `python main.py` al final: menú, simulación completa con pausas visibles y una partida interactiva
  hasta el FIN.
