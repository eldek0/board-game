import pygame
import time
import pygame_gui
from pygame.locals import QUIT

import random

import files.draw as dr
import game.gui as gui
from files.mouse import Mouse
from files.import_imp import import_images
from files.utils import player_colors
from game.state import Player, GameState
from game.rules import play_turn

def do_action(string, another):
	print("STRING: " + string)
	print("THE OTHER: " + str(another))


class App:
	def __init__(self, initial_dimentions=(1080, 720), caption="App", players=2, seed=42):
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

		# Partida
		colors = player_colors(players, seed)
		self.game_state = GameState(
			players=tuple(
				Player(name=f"Player {i+1}", color=colors[i])
				for i in range(players)
			),
			rng=random.Random(seed),
		)
		self.last_roll = None

		# Widgets
		self.ui_manager = pygame_gui.UIManager(self.dimentions)
		gui.create_game_ui(self)

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

			self.ui_manager.update(self.deltaTime)

			self.game_events(events)

			self.update(events)

	def game_events(self, events):
		for event in events:
			if event.type == QUIT:
				self.playing = False

			elif event.type == pygame.VIDEORESIZE:
				self.dimentions = (event.w, event.h)
				self.surface = pygame.display.set_mode(self.dimentions, pygame.RESIZABLE)
				self.ui_manager.set_window_resolution(self.dimentions)
				gui.layout_game_ui(self)

			elif event.type == pygame_gui.UI_BUTTON_PRESSED:
				if event.ui_element == self.btn_roll:
					self.roll_dice()

			self.ui_manager.process_events(event)
				
	def roll_dice(self):
		if self.game_state.winner:
			return

		self.last_roll = self.game_state.rng.randint(1, 6)
		self.game_state = play_turn(self.game_state, self.last_roll)

		if self.game_state.winner:
			self.btn_roll.disable()

	def update(self, events):
		self.surface.fill((105,105,105))

		# Draw on screen
		dr.Draw(self)
		self.ui_manager.draw_ui(self.surface)

		# Update each frame
		pygame.display.update()

