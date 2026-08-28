from __future__ import annotations
from typing import TYPE_CHECKING

import pygame

import files.utils as f

if TYPE_CHECKING:
	from files.app_main import App

def Draw(app:App):
	if app.scene == 0:
		#app.surface.blit(app.assets.pygame_spr, (0, 0))
		#f.text(app.surface, "HOla", (0,0), app.assets.Arial60, (0, 0, 150))

		pygame.draw.line(app.surface, (0, 0, 0), (0, 0), (200, 200), width=2)