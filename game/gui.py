from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING: from files.app_main import App

import pygame
import pygame_gui

from game.board import PATH, SPECIAL, START, END, ROWS, COLS, coord
import files.utils as f

# Board cell size and roll-button geometry, in pixels
CELL = 64
BTN_W, BTN_H, BTN_GAP = 170, 44, 16
PLAYER_RADIUS = 10

def board_origin(width: int, height: int) -> tuple[int, int]:
	"""Top left corner that leaves the board centered in the window."""
	return ((width - COLS * CELL) // 2, (height - ROWS * CELL) // 2)

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
			pygame.draw.circle(app.surface, player.color, center, PLAYER_RADIUS)
			pygame.draw.circle(app.surface, (0, 0, 0), center, PLAYER_RADIUS, width=1)

def button_rect(width: int, height: int, slot: int = 0) -> pygame.Rect:
	"""The roll/reset buttons, stacked right below the board (slot 0 = top)."""
	origin = board_origin(width, height)
	x = origin[0] + (COLS * CELL - BTN_W) // 2
	y = origin[1] + ROWS * CELL + BTN_GAP + slot * (BTN_H + BTN_GAP)
	return pygame.Rect(x, y, BTN_W, BTN_H)

def create_game_ui(app:App):
	"""Creates widgets when scene starts"""
	app.btn_roll = pygame_gui.elements.UIButton(
		relative_rect=button_rect(*app.surface.get_size(), slot=0),
		text="Tirar dado",
		manager=app.ui_manager)
	app.btn_reset = pygame_gui.elements.UIButton(
		relative_rect=button_rect(*app.surface.get_size(), slot=1),
		text="Reiniciar",
		manager=app.ui_manager)

def layout_game_ui(app:App):
	"""Repositions widgets when the window is resized"""
	app.btn_roll.set_relative_position(button_rect(*app.surface.get_size(), slot=0).topleft)
	app.btn_reset.set_relative_position(button_rect(*app.surface.get_size(), slot=1).topleft)

def draw_hud(app:App):
	origin = board_origin(*app.surface.get_size())
	state = app.game_state

	# Left: whose turn it is, or the winner once the game is over
	if state.winner:
		status = f"Gano {state.winner.name}"
	else:
		status = f"Turno {state.turn + 1}"

	# Right: last rolled value, a dash before the first roll
	dice = "-" if app.last_roll is None else str(app.last_roll)

	f.text(app.surface, status, (origin[0], origin[1] - 36), app.assets.Arial30, (255, 255, 255))
	f.text(app.surface, f"Dado: {dice}", (origin[0] + COLS * CELL - 110, origin[1] - 36),
		app.assets.Arial30, (255, 255, 255))

def draw_game(app:App):
	draw_board(app)
	draw_players(app)
	draw_hud(app)
