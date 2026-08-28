from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING: from files.app_main import App

import pygame
import pygame_gui

from game.board import PATH, SPECIAL, START, END, ROWS, COLS
import files.utils as f

# Board cell size and roll-button geometry, in pixels
CELL = 64
BTN_W, BTN_H, BTN_GAP = 170, 44, 16

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
	if label:
		f.text_centered(app.surface, label, rect, app.assets.Arial16, (0, 0, 0))

	draw_board(app, n=n+1, origin=origin)

def button_rect(width: int, height: int) -> pygame.Rect:
	"""The roll button, centered right below the board."""
	origin = board_origin(width, height)
	x = origin[0] + (COLS * CELL - BTN_W) // 2
	y = origin[1] + ROWS * CELL + BTN_GAP
	return pygame.Rect(x, y, BTN_W, BTN_H)

def create_game_ui(app:App):
	"""Creates widgets when scene starts"""
	app.btn_roll = pygame_gui.elements.UIButton(
		relative_rect=button_rect(*app.surface.get_size()),
		text="Tirar dado",
		manager=app.ui_manager)

def layout_game_ui(app:App):
	"""Repositions widgets when the window is resized"""
	app.btn_roll.set_relative_position(button_rect(*app.surface.get_size()).topleft)

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
	draw_hud(app)
