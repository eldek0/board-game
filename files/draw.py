import pygame

import files.utils as f

def Draw(app:App):
	if app.scene == 0:
		app.surface.blit(app.assets.pygame_spr, (0, 0))
		f.text(app.surface, "HOla", (0,0), app.assets.Arial60, (0, 0, 150))