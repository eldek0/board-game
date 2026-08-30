from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING: from files.app_main import App

import html

import pygame
import pygame_gui

from game.board import PATH, SPECIAL, START, END, ROWS, COLS, coord
from game import log as game_log
import files.utils as f

# Board cell size and roll-button geometry, in pixels
CELL = 64
DICE_SIZE = 130        # on-screen side of the die drawn inside the board
BG_SPEED = 40          # background scroll, pixels per second
TEXT_COLOR = (35, 35, 40)

# Board cell fills: plain cells are white, the rest are grouped by meaning so a
# reward and a punishment read apart at a glance, with the label naming which one.
CELL_COLOR = (255, 255, 255)
CELL_BORDER = (0, 0, 0)
START_COLOR = (150, 190, 240)      # INICIO, blue
END_COLOR = (245, 205, 105)        # FIN, gold
REWARD_COLOR = (150, 220, 160)     # P1 P2 P3, green
PUNISH_COLOR = (240, 155, 155)     # C1 C2, red

SPECIAL_COLORS = {
	"P1": REWARD_COLOR,
	"P2": REWARD_COLOR,
	"P3": REWARD_COLOR,
	"C1": PUNISH_COLOR,
	"C2": PUNISH_COLOR,
}
ERROR_COLOR = (170, 30, 30)
BTN_W, BTN_H, BTN_GAP = 170, 44, 16
MENU_BTN_MARGIN = 20
PLAYER_RADIUS = 10
# Log box: fixed size, sits to the right of the board and vertically centered on it
LOG_W, LOG_H, LOG_GAP = 250, 460, 16
NAME_INPUT_W = 320
NAME_INPUT_H = 44
NAME_GAP = 70

def form_rects(width: int, height: int):
	"""Two stacked input fields plus a button, centered. Shared by the name and
	simulation-config screens, so both forms line up identically."""
	cx = width // 2
	start_y = height // 2 - 70

	return (
		pygame.Rect(
			cx - NAME_INPUT_W // 2,
			start_y,
			NAME_INPUT_W,
			NAME_INPUT_H
		),

		pygame.Rect(
			cx - NAME_INPUT_W // 2,
			start_y + NAME_GAP,
			NAME_INPUT_W,
			NAME_INPUT_H
		),

		pygame.Rect(
			cx - BTN_W // 2,
			start_y + NAME_GAP * 2,
			BTN_W,
			BTN_H
		),
	)

def draw_background(app:App):
	"""Tiles the dice pattern across the window, sliding it sideways over time.

	The offset wraps at the image width, so one extra column drawn past the right
	edge is enough to keep the loop seamless.
	"""
	image = app.assets.background
	tile_w, tile_h = image.get_size()
	width, height = app.surface.get_size()

	start_x = -(app.bg_offset % tile_w)

	x = start_x
	while x < width:
		y = 0
		while y < height:
			app.surface.blit(image, (x, y))
			y += tile_h
		x += tile_w

def board_origin(width: int, height: int) -> tuple[int, int]:
	"""Top left of the board so the board + log box together sit centered in the window."""
	group_w = COLS * CELL + LOG_GAP + LOG_W
	return ((width - group_w) // 2, (height - ROWS * CELL) // 2)

def cell_rect(row: int, col:int, origin:tuple[int, int]) -> pygame.Rect:
	return pygame.Rect(origin[0] + col * CELL, origin[1] + row * CELL, CELL, CELL)

def cell_label(i: int) -> str | None:
    if i == START: return "INICIO"
    if i == END:   return "FIN"
    return SPECIAL.get(i)

def cell_color(i: int) -> tuple[int, int, int]:
	"""Fill color for cell i: white unless it is INICIO, FIN, a reward or a punishment."""
	if i == START: return START_COLOR
	if i == END:   return END_COLOR
	return SPECIAL_COLORS.get(SPECIAL.get(i), CELL_COLOR)

def draw_board(app:App, n=0, origin:tuple[int, int]=None):
	if origin is None:
		origin = board_origin(*app.surface.get_size())

	if n >= len(PATH):
		return

	row, col = PATH[n]
	rect = cell_rect(row, col, origin)

	pygame.draw.rect(
		surface=app.surface,
		rect=rect,
		color=cell_color(n)
	)

	pygame.draw.rect(
		surface=app.surface,
		rect=rect,
		color=CELL_BORDER,
		width=3
	)

	label = cell_label(n)
	if n == START:
		f.text_centered(app.surface, label, rect, app.assets.Arial24, (0, 0, 0))
	elif label:
		f.text_centered(app.surface, label, rect, app.assets.Arial30, (0, 0, 0))

	draw_board(app, n=n+1, origin=origin)

def token_position(rect: pygame.Rect, index: int, total: int) -> tuple[int, int]:
	"""Center for the index-th token sharing a cell, nudged sideways so stacked players stay visible."""
	cx, cy = rect.center
	offset = (index - (total - 1) / 2) * (PLAYER_RADIUS + 2)
	return (int(cx + offset), cy)

_dice_scaled: dict[int, pygame.Surface] = {}

def dice_image(app:App, value: int) -> pygame.Surface:
	"""The die face for value, scaled to DICE_SIZE. Cached: at most six entries."""
	if value not in _dice_scaled:
		_dice_scaled[value] = pygame.transform.smoothscale(
			app.assets.dice[value], (DICE_SIZE, DICE_SIZE))
	return _dice_scaled[value]

def draw_dice(app:App, origin:tuple[int, int]=None):
	"""Draws the last rolled die in the hollow middle of the board."""
	if app.last_roll is None:
		return

	if origin is None:
		origin = board_origin(*app.surface.get_size())

	image = dice_image(app, app.last_roll)
	rect = image.get_rect(
		center=(origin[0] + COLS * CELL // 2, origin[1] + ROWS * CELL // 2))

	# The sprite is only the black outline and pips, so the face is painted here
	pygame.draw.rect(app.surface, CELL_COLOR, rect)
	app.surface.blit(image, rect)

def draw_players(app:App, origin:tuple[int, int]=None):
	"""Draws every player as a colored token on the cell matching its current position."""
	if origin is None:
		surface_size = app.surface.get_size()
		origin = board_origin(surface_size[0], surface_size[1])

	players_by_position: dict[int, list] = {}
	for player in app.game_state.players:
		players_by_position.setdefault(player.position, []).append(player)

	for position, players in players_by_position.items():
		row, col = coord(position)
		rect = cell_rect(row, col, origin)
		total = len(players)

		for index, player in enumerate(players):
			center = token_position(rect, index, total)
			pygame.draw.circle(
				app.surface, 
				player.color, 
				center, 
				PLAYER_RADIUS)
			
			pygame.draw.circle(
				app.surface, 
				(0, 0, 0), 
				center, 
				PLAYER_RADIUS, 
				width=1)

			#para que el nombre del jugador se vea encima de la ficha
			name_img = app.assets.Arial18.render(
				player.name,
				True,
				TEXT_COLOR
			)
			name_rect = name_img.get_rect(
				midbottom= (
					center[0],
					center[1] - PLAYER_RADIUS - 4
				)
			)
			app.surface.blit(name_img, name_rect)


				
def button_rect(width: int, height: int, slot: int = 0) -> pygame.Rect:
	"""The roll/reset buttons, stacked right below the board (slot 0 = top)."""
	origin = board_origin(width, height)
	x = origin[0] + (COLS * CELL - BTN_W) // 2
	y = origin[1] + ROWS * CELL + BTN_GAP + slot * (BTN_H + BTN_GAP)
	return pygame.Rect(x, y, BTN_W, BTN_H)

def menu_button_rect(width: int, height: int) -> pygame.Rect:
	"""The back-to-menu button, pinned to the top left corner of the window."""
	return pygame.Rect(MENU_BTN_MARGIN, MENU_BTN_MARGIN, BTN_W, BTN_H)

def console_rect(width: int, height: int) -> pygame.Rect:
	"""The log box: fixed size, glued to the right of the board and centered on its height."""
	origin = board_origin(width, height)
	x = origin[0] + COLS * CELL + LOG_GAP
	y = origin[1] + (ROWS * CELL - LOG_H) // 2
	return pygame.Rect(x, y, LOG_W, LOG_H)


def create_name_ui(app:App):
	input1_rect, input2_rect, start_rect = form_rects(
		*app.surface.get_size()
	)

	app.input_player1 = pygame_gui.elements.UITextEntryLine(
		relative_rect=input1_rect,
		manager=app.ui_manager
	)

	app.input_player1.set_text_length_limit(16)

	app.input_player2 = pygame_gui.elements.UITextEntryLine(
		relative_rect=input2_rect,
		manager=app.ui_manager
	)

	app.input_player2.set_text_length_limit(16)

	app.btn_start = pygame_gui.elements.UIButton(
		relative_rect=start_rect,
		text="Comenzar",
		manager=app.ui_manager
	)

def create_sim_config_ui(app:App):
	"""Seed and player-count fields shown before a simulation starts."""
	seed_rect, players_rect, start_rect = form_rects(*app.surface.get_size())

	app.input_seed = pygame_gui.elements.UITextEntryLine(
		relative_rect=seed_rect,
		manager=app.ui_manager
	)
	app.input_seed.set_allowed_characters("numbers")
	app.input_seed.set_text_length_limit(9)

	app.input_players = pygame_gui.elements.UITextEntryLine(
		relative_rect=players_rect,
		manager=app.ui_manager
	)
	app.input_players.set_allowed_characters("numbers")
	app.input_players.set_text_length_limit(1)

	app.btn_sim_start = pygame_gui.elements.UIButton(
		relative_rect=start_rect,
		text="Comenzar",
		manager=app.ui_manager
	)

def create_game_ui(app:App):
	"""Creates widgets when scene starts"""
	app.btn_roll = pygame_gui.elements.UIButton(
		relative_rect=button_rect(*app.surface.get_size(), slot=0),
		text="Tirar dado (Espacio)",
		manager=app.ui_manager)
	app.btn_reset = pygame_gui.elements.UIButton(
		relative_rect=button_rect(*app.surface.get_size(), slot=1),
		text="Reiniciar",
		manager=app.ui_manager)
	app.btn_new_sim = pygame_gui.elements.UIButton(
		relative_rect=button_rect(*app.surface.get_size(), slot=1),
		text="Nueva partida",
		manager=app.ui_manager)
	app.btn_menu = pygame_gui.elements.UIButton(
		relative_rect=menu_button_rect(*app.surface.get_size()),
		text="Volver al menu",
		manager=app.ui_manager)
	app.log_box = pygame_gui.elements.UITextBox(
		html_text="".join(f"{html.escape(line)}<br>" for line in game_log.lines()),
		relative_rect=console_rect(*app.surface.get_size()),
		manager=app.ui_manager)
	game_log.drain()

def mode_ui_rects(width: int, height: int) -> tuple[pygame.Rect, pygame.Rect]:
	"""The two mode buttons, stacked and centered in the window."""
	x = width // 2 - BTN_W // 2
	return (
		pygame.Rect(x, height // 2 - 30, BTN_W, BTN_H),
		pygame.Rect(x, height // 2 + 40, BTN_W, BTN_H),
	)

def create_mode_ui(app:App):
	interactive_rect, simulation_rect = mode_ui_rects(*app.surface.get_size())

	app.btn_interactive = pygame_gui.elements.UIButton(
		relative_rect=interactive_rect,
		text="Interactivo",
		manager=app.ui_manager
	)

	app.btn_simulation = pygame_gui.elements.UIButton(
		relative_rect=simulation_rect,
		text="Simulacion",
		manager=app.ui_manager
	)

def draw_mode_screen(app:App):
	width, height = app.surface.get_size()

	interactive_rect, _ = mode_ui_rects(width, height)

	title_rect = pygame.Rect(
		0,
		interactive_rect.top - 90,
		width,
		70
	)

	f.text_centered(
		app.surface,
		"Seleccione un modo de juego",
		title_rect,
		app.assets.Arial60,
		TEXT_COLOR
	)


def show_name_ui(app:App):
	app.btn_interactive.hide()
	app.btn_simulation.hide()

	app.input_player1.show()
	app.input_player2.show()
	app.btn_start.show()

	app.input_seed.hide()
	app.input_players.hide()
	app.btn_sim_start.hide()

	app.btn_roll.hide()
	app.btn_reset.hide()
	app.btn_new_sim.hide()
	app.btn_menu.hide()
	app.log_box.hide()

def show_mode_ui(app:App):
	app.btn_interactive.show()
	app.btn_simulation.show()

	app.input_player1.hide()
	app.input_player2.hide()
	app.btn_start.hide()

	app.input_seed.hide()
	app.input_players.hide()
	app.btn_sim_start.hide()

	app.btn_roll.hide()
	app.btn_reset.hide()
	app.btn_new_sim.hide()
	app.btn_menu.hide()

	app.log_box.hide()

def show_game_ui(app:App):
	app.btn_interactive.hide()
	app.btn_simulation.hide()

	app.input_player1.hide()
	app.input_player2.hide()
	app.btn_start.hide()

	app.input_seed.hide()
	app.input_players.hide()
	app.btn_sim_start.hide()

	app.btn_roll.show()
	app.btn_reset.show()
	app.btn_new_sim.hide()
	app.btn_menu.show()
	app.log_box.show()

	layout_game_ui(app)

def show_simulation_ui(app:App):
	app.btn_interactive.hide()
	app.btn_simulation.hide()

	app.input_player1.hide()
	app.input_player2.hide()
	app.btn_start.hide()

	app.input_seed.hide()
	app.input_players.hide()
	app.btn_sim_start.hide()

	app.btn_roll.hide()
	app.btn_reset.show()
	app.btn_new_sim.show()
	app.btn_menu.show()

	app.log_box.show()

	layout_game_ui(app)

def show_sim_config_ui(app:App):
	app.btn_interactive.hide()
	app.btn_simulation.hide()

	app.input_player1.hide()
	app.input_player2.hide()
	app.btn_start.hide()

	app.input_seed.show()
	app.input_players.show()
	app.btn_sim_start.show()

	app.btn_roll.hide()
	app.btn_reset.hide()
	app.btn_new_sim.hide()
	app.btn_menu.show()
	app.log_box.hide()

def layout_game_ui(app:App):
	"""Repositions widgets when the window is resized or the scene changes.

	In simulation mode the roll button is hidden, so reset takes its slot instead
	of leaving a gap under the board.
	"""
	size = app.surface.get_size()
	reset_slot = 0 if app.simulation_mode else 1

	app.btn_roll.set_relative_position(button_rect(*size, slot=0).topleft)
	app.btn_reset.set_relative_position(button_rect(*size, slot=reset_slot).topleft)
	app.btn_new_sim.set_relative_position(button_rect(*size, slot=reset_slot + 1).topleft)
	app.btn_menu.set_relative_position(menu_button_rect(*size).topleft)
	app.log_box.set_relative_position(console_rect(*size).topleft)

def scroll_console_to_bottom(app:App):
	"""Pins the log box to its newest line.

	pygame_gui's append_html_text writes scroll_position straight onto the scroll bar
	without moving its sliding button, so the bar drifts out of sync with the text and
	the last lines end up hidden. Going through the bar's own API fixes all of it; the
	1.0 is clamped to the real bottom internally.
	"""
	bar = app.log_box.scroll_bar
	if bar is not None:
		bar.set_scroll_from_start_percentage(1.0)

def sync_console(app:App):
	"""Pushes any freshly logged game events into the log box; call once per frame."""
	new_lines = game_log.drain()
	if new_lines:
		app.log_box.append_html_text("".join(f"{html.escape(line)}<br>" for line in new_lines))
		scroll_console_to_bottom(app)

def draw_hud(app:App):
	origin = board_origin(*app.surface.get_size())
	state = app.game_state

	# Left: whose turn it is, or the winner once the game is over
	if state.winner:
		status = f"Gano {state.winner.name}"
	else:
		current_player = state.players[
			state.turn % len(state.players)
		]
		status = f"Turno {state.turn + 1}"

	# Right: last rolled value, a dash before the first roll
	dice = "-" if app.last_roll is None else str(app.last_roll)

	f.text(
		app.surface, 
		status, 
		(origin[0], origin[1] - 36), 
		app.assets.Arial30, TEXT_COLOR)
	
	f.text(
		app.surface, 
		f"Dado: {dice}",
		(origin[0] + COLS * CELL - 110, origin[1] - 36),
		app.assets.Arial30, 
		TEXT_COLOR)





def draw_name_screen(app:App):
	width, height = app.surface.get_size()

	input1_rect, input2_rect, _ = form_rects(
		width,
		height
	)

	title_rect = pygame.Rect(
		0,
		input1_rect.top - 110,
		width,
		60
	)

	f.text_centered(
		app.surface,
		"Modo interactivo",
		title_rect,
		app.assets.Arial60,
		TEXT_COLOR
	)

	f.text(
		app.surface,
		"Nombre jugador 1",
		(input1_rect.left, input1_rect.top - 30),
		app.assets.Arial24,
		TEXT_COLOR
	)

	f.text(
		app.surface,
		"Nombre jugador 2",
		(input2_rect.left, input2_rect.top - 30),
		app.assets.Arial24,
		TEXT_COLOR
	)

	if app.name_error:
		error_rect = pygame.Rect(
			0,
			input2_rect.bottom + 105,
			width,
			40
		)

		f.text_centered(
			app.surface,
			app.name_error,
			error_rect,
			app.assets.Arial24,
			ERROR_COLOR
		)
def layout_ui(app:App):
	interactive_rect, simulation_rect = mode_ui_rects(*app.surface.get_size())

	app.btn_interactive.set_relative_position(interactive_rect.topleft)
	app.btn_simulation.set_relative_position(simulation_rect.topleft)

	input1_rect, input2_rect, start_rect = form_rects(
		*app.surface.get_size()
	)

	app.input_player1.set_relative_position(
		input1_rect.topleft
	)

	app.input_player2.set_relative_position(
		input2_rect.topleft
	)

	app.btn_start.set_relative_position(
		start_rect.topleft
	)

	app.input_seed.set_relative_position(input1_rect.topleft)
	app.input_players.set_relative_position(input2_rect.topleft)
	app.btn_sim_start.set_relative_position(start_rect.topleft)

	layout_game_ui(app)


def draw_sim_config_screen(app:App):
	width, height = app.surface.get_size()
	seed_rect, players_rect, _ = form_rects(width, height)

	f.text_centered(
		app.surface,
		"Modo simulacion",
		pygame.Rect(0, seed_rect.top - 110, width, 60),
		app.assets.Arial60,
		TEXT_COLOR
	)

	f.text(
		app.surface,
		"Semilla (vacia = aleatoria)",
		(seed_rect.left, seed_rect.top - 30),
		app.assets.Arial24,
		TEXT_COLOR
	)

	f.text(
		app.surface,
		"Cantidad de jugadores (2-4)",
		(players_rect.left, players_rect.top - 30),
		app.assets.Arial24,
		TEXT_COLOR
	)

	if app.sim_error:
		f.text_centered(
			app.surface,
			app.sim_error,
			pygame.Rect(0, players_rect.bottom + 105, width, 40),
			app.assets.Arial24,
			ERROR_COLOR
		)

def draw_console_title(app:App):
	"""Heading shown just above the log box."""
	box = console_rect(*app.surface.get_size())
	f.text(app.surface, "Historial de Partida", (box.x, box.y - 28), app.assets.Arial24, TEXT_COLOR)

def draw_game(app:App):
	draw_board(app)
	draw_dice(app)
	draw_players(app)
	draw_hud(app)
	draw_console_title(app)
