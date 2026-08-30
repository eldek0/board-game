import pygame
from pygame.locals import *

# Layout of sprites/dice.png: a 3x2 grid of square faces
DICE_CELL = 300
DICE_SHEET = (
	(4, 1, 6),
	(5, 3, 2),
)

class import_images:

	def __init__(self):
		import_images.images(self)
		
		import_images.audios(self)

		import_images.fonts(self)

		print("Assets loaded!")

	def cropped_images(self):
		"""Slices the dice sheet into one surface per face, keyed by its value.

		sprites/dice.png is a 3x2 grid of 300x300 faces laid out like this:
			row 0: 4 1 6
			row 1: 5 3 2
		"""
		self.dice = {
			value: self.dice_spr.subsurface(
				pygame.Rect(col * DICE_CELL, row * DICE_CELL, DICE_CELL, DICE_CELL)
			)
			for row, sheet_row in enumerate(DICE_SHEET)
			for col, value in enumerate(sheet_row)
		}

	def images(self):
		# Images
		self.pygame_spr = pygame.image.load("sprites/pygame.png").convert_alpha()

		pattern = pygame.image.load("sprites/background.png").convert_alpha()
		pattern.set_alpha(120)

		self.background = pygame.Surface(pattern.get_size()).convert()
		self.background.fill((238, 238, 243))
		self.background.blit(pattern, (0, 0))

		# Dices
		# dice.png is ink on transparency: its palette is entirely black and the
		# face is the transparent part, so it needs the alpha channel kept.
		self.dice_spr = pygame.image.load("sprites/dice.png").convert_alpha()

		# Get crops from cropped images
		import_images.cropped_images(self)
		
				
	def audios(self):
		pass

	def fonts(self):
		self.Arial = "fonts/arial.ttf"

		# get font types
		self.font_types()

	def font_types(self):
		self.Arial60 = pygame.font.Font(self.Arial, 60)
		self.Arial30 = pygame.font.Font(self.Arial, 30)
		self.Arial24 = pygame.font.Font(self.Arial, 24)
		self.Arial16 = pygame.font.Font(self.Arial, 16)
		self.Arial18 = pygame.font.Font(self.Arial, 18)
