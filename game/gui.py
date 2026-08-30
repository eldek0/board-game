from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING: from files.app_main import App

import html
import io
import json

import pygame
import pygame_gui

from game.board import PATH, SPECIAL, START, END, ROWS, COLS, coord
from game import log as game_log
import files.utils as f

# Board cell size and roll-button geometry, in pixels
CELL = 64
BTN_W, BTN_H, BTN_GAP = 170, 44, 16
PLAYER_RADIUS = 10
# Log box: fixed size, sits to the right of the board and vertically centered on it
LOG_W, LOG_H, LOG_GAP = 250, 460, 16
LOG_FONT_SIZE = 10  # point size of the text inside the log box
NAME_INPUT_W = 320
NAME_INPUT_H = 44
NAME_GAP = 70

def name_ui_rects(width: int, height: int):
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
		color=(250, 150, 150), 
		width=1
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
				(255, 255, 255)
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

def console_rect(width: int, height: int) -> pygame.Rect:
	"""The log box: fixed size, glued to the right of the board and centered on its height."""
	origin = board_origin(width, height)
	x = origin[0] + COLS * CELL + LOG_GAP
	y = origin[1] + (ROWS * CELL - LOG_H) // 2
	return pygame.Rect(x, y, LOG_W, LOG_H)


def create_name_ui(app:App):
	input1_rect, input2_rect, start_rect = name_ui_rects(
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

def create_game_ui(app:App):
	"""Creates widgets when scene starts"""
	# Set the log box text size (pygame_gui fonts are theme-driven)
	app.ui_manager.get_theme().load_theme(
		io.StringIO(json.dumps({"text_box": {"font": {"size": LOG_FONT_SIZE}}})))

	app.btn_roll = pygame_gui.elements.UIButton(
		relative_rect=button_rect(*app.surface.get_size(), slot=0),
		text="Tirar dado",
		manager=app.ui_manager)
	app.btn_reset = pygame_gui.elements.UIButton(
		relative_rect=button_rect(*app.surface.get_size(), slot=1),
		text="Reiniciar",
		manager=app.ui_manager)
	app.log_box = pygame_gui.elements.UITextBox(
		html_text="".join(f"{html.escape(line)}<br>" for line in game_log.lines()),
		relative_rect=console_rect(*app.surface.get_size()),
		manager=app.ui_manager)
	game_log.drain()

def create_mode_ui(app:App):
	width, height = app.surface.get_size()

	app.btn_interactive = pygame_gui.elements.UIButton(
		relative_rect=pygame.Rect(
			width // 2 - BTN_W // 2,
			height // 2 - 30,
			BTN_W,
			BTN_H
		),
		text="Interactivo",
		manager=app.ui_manager
	)

	app.btn_simulation = pygame_gui.elements.UIButton(
		relative_rect=pygame.Rect(
			width // 2 - BTN_W // 2,
			height // 2 + 40,
			BTN_W,
			BTN_H
		),
		text="Simulacion",
		manager=app.ui_manager
	)

def draw_mode_screen(app:App):
	width, height = app.surface.get_size()

	title_rect = pygame.Rect(
		0,
		height // 2 - 120,
		width,
		70
	)

	f.text_centered(
		app.surface,
		"Seleccione un modo de juego",
		title_rect,
		app.assets.Arial60,
		(255, 255, 255)
	)


def show_name_ui(app:App):
	app.btn_interactive.hide()
	app.btn_simulation.hide()

	app.input_player1.show()
	app.input_player2.show()
	app.btn_start.show()

	app.btn_roll.hide()
	app.btn_reset.hide()
	app.log_box.hide()

def show_mode_ui(app:App):
	app.btn_interactive.show()
	app.btn_simulation.show()

	app.input_player1.hide()
	app.input_player2.hide()
	app.btn_start.hide()

	app.btn_roll.hide()
	app.btn_reset.hide()

	app.log_box.hide()

def show_game_ui(app:App):
	app.btn_interactive.hide()
	app.btn_simulation.hide()

	app.input_player1.hide()
	app.input_player2.hide()
	app.btn_start.hide()

	app.btn_roll.show()
	app.btn_reset.show()
	app.log_box.show()

def show_simulation_ui(app:App):
	app.btn_interactive.hide()
	app.btn_simulation.hide()

	app.input_player1.hide()
	app.input_player2.hide()
	app.btn_start.hide()

	app.btn_roll.hide()
	app.btn_reset.show()

	app.log_box.show()

def layout_game_ui(app:App):
	"""Repositions widgets when the window is resized"""
	app.btn_roll.set_relative_position(button_rect(*app.surface.get_size(), slot=0).topleft)
	app.btn_reset.set_relative_position(button_rect(*app.surface.get_size(), slot=1).topleft)
	app.log_box.set_relative_position(console_rect(*app.surface.get_size()).topleft)

def sync_console(app:App):
	"""Pushes any freshly logged game events into the log box; call once per frame."""
	new_lines = game_log.drain()
	if new_lines:
		app.log_box.append_html_text("".join(f"{html.escape(line)}<br>" for line in new_lines))

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
		app.assets.Arial30, (255, 255, 255))
	
	f.text(
		app.surface, 
		f"Dado: {dice}",
		(origin[0] + COLS * CELL - 110, origin[1] - 36),
		app.assets.Arial30, 
		(255, 255, 255))





def draw_name_screen(app:App):
	width, height = app.surface.get_size()

	input1_rect, input2_rect, _ = name_ui_rects(
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
		(255, 255, 255)
	)

	f.text(
		app.surface,
		"Nombre jugador 1",
		(input1_rect.left, input1_rect.top - 30),
		app.assets.Arial24,
		(255, 255, 255)
	)

	f.text(
		app.surface,
		"Nombre jugador 2",
		(input2_rect.left, input2_rect.top - 30),
		app.assets.Arial24,
		(255, 255, 255)
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
			(255, 210, 210)
		)
def layout_ui(app:App):
	input1_rect, input2_rect, start_rect = name_ui_rects(
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

	layout_game_ui(app)


def draw_console_title(app:App):
	"""Heading shown just above the log box."""
	box = console_rect(*app.surface.get_size())
	f.text(app.surface, "Historial de Partida", (box.x, box.y - 28), app.assets.Arial24, (255, 255, 255))

def draw_game(app:App):
	draw_board(app)
	draw_players(app)
	draw_hud(app)
	draw_console_title(app)
