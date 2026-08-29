from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING: from files.app_main import App

import pygame

import game.gui as gui

def Draw(app:App):
	if app.scene == 0:
		gui.draw_name_screen(app)

	elif app.scene == 1:
		gui.draw_game(app)