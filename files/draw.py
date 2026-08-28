import pygame

import files.utils as f

def Draw(App):
	if App.scene == 0:
		App.surface.blit(App.assets.pygame_spr, (0, 0))