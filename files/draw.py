from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING: from files.app_main import App

import pygame

import files.gui as gui

def Draw(app:App):
	gui.draw_background(app)

	if app.scene == 0:
		gui.draw_mode_screen(app)

	elif app.scene == 1:
		gui.draw_name_screen(app)

	elif app.scene == 2:
		gui.draw_game(app)

	elif app.scene == 3:
		gui.draw_sim_config_screen(app)