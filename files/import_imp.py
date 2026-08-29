import pygame
from pygame.locals import *

class import_images:

	def __init__(self):
		import_images.images(self)
		
		import_images.audios(self)

		import_images.fonts(self)

		print("Assets loaded!")

	def cropped_images(self):
		pass

	def images(self):
		# Images
		self.pygame_spr = pygame.image.load("sprites/pygame.png").convert_alpha()

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