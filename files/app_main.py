import pygame
import time
from pygame.locals import QUIT

import files.draw as dr
from files.mouse import Mouse
from files.import_imp import import_images

def do_action(string, another):
	print("STRING: " + string)
	print("THE OTHER: " + str(another))


class App:
	def __init__(self, initial_dimentions=(1080, 720), caption="App"):
		self.playing = True

		# Surface init
		pygame.init()
		self.dimentions = initial_dimentions
		self.surface = pygame.display.set_mode( self.dimentions, pygame.RESIZABLE )
		pygame.display.set_caption(caption) # Win's name

		# Fps configurations
		self.clock = pygame.time.Clock()
		self.frames_per_second = 60

		self.assets = import_images()
		self.scene = 0

		# Mouse
		self.mouse_control = Mouse()

		# DeltaTime variables
		self.prev_time, self.now_time = time.time(), time.time()

	def get_deltatime(self):
		self.now_time = time.time()
		self.deltaTime = self.now_time - self.prev_time
		self.prev_time = self.now_time

	def loop(self):
		while self.playing == True:
			
			events = pygame.event.get()

			# Update mouse's hitbox and pressed buttons
			self.mouse_control.mouse_update()

			# Frames per second
			self.game_fps = self.clock.tick(self.frames_per_second)

			#DeltaTime
			self.get_deltatime()

			self.game_events(events)

			self.update(events)

	def game_events(self, events):
		for event in events:
			if event.type == QUIT:
				self.playing = False
				
	def update(self, events):
		self.surface.fill((105,105,105))

		# Draw on screen
		dr.Draw(self)

		# Update each frame
		pygame.display.update()

