import pygame
import time
from pygame import event
import pygame_gui
from pygame.locals import QUIT

import random

import files.draw as dr
import game.gui as gui
from game import log as game_log
from files.mouse import Mouse
from files.import_imp import import_images
from files.utils import player_colors
from game.state import Player, GameState
from game.rules import play_turn

class App:
	def __init__(self, initial_dimentions=(1080, 920), caption="App", players=2, seed=42):
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
		self.name_error =  ""

		# Mouse
		self.mouse_control = Mouse()

		# DeltaTime variables
		self.prev_time, self.now_time = time.time(), time.time()

		# Partida
		self.num_players = players
		self.seed = seed
		self.player_names = tuple(
			f"Player {i+1}" for i in range(self.num_players)
		)
		self.new_game()

		# Widgets
		self.ui_manager = pygame_gui.UIManager(self.dimentions)
		gui.create_game_ui(self)
		gui.create_name_ui(self)
		gui.show_name_ui(self)

	def new_game(self):
		colors = (
			(50, 130, 255),   # jugador 1 azul
			(255, 190, 50),   # jugador 2 amarillo
		)
		self.game_state = GameState(
			players=tuple(
				Player(
					name=self.player_names[i], 
		   			color=colors[i]
				)
				for i in range(self.num_players)
			),
			rng=random.Random(self.seed),
		)
		self.last_roll = None

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

			gui.sync_console(self)
			self.ui_manager.update(self.deltaTime)

			self.update(events)

	def game_events(self, events):
		for event in events:
			if event.type == QUIT:
				self.playing = False

			elif event.type == pygame.VIDEORESIZE:
				self.dimentions = (event.w, event.h)
				self.surface = pygame.display.set_mode(self.dimentions, pygame.RESIZABLE)
				self.ui_manager.set_window_resolution(self.dimentions)
				gui.layout_ui(self)

			elif event.type == pygame_gui.UI_BUTTON_PRESSED:
				if event.ui_element == self.btn_start:
					self.start_interactive_game()
				elif event.ui_element == self.btn_roll:
					self.roll_dice()
				elif event.ui_element == self.btn_reset:
					self.reset_game()

			self.ui_manager.process_events(event)

	def reset_game(self):
		self.new_game()
		self.btn_roll.enable()
		game_log.clear()
		self.log_box.set_text("")


	def start_interactive_game(self):
		name1 = self.input_player1.get_text().strip()
		name2 = self.input_player2.get_text().strip()	

		if not name1 or not name2:
			self.name_error = "Ambos jugadores deben tener nombre"
			return

		
		if name1.lower() == name2.lower():
			self.name_error = "Los jugadores deben tener nombres diferentes."
			return


		self.player_names = (name1, name2)
		self.name_error = ""
		self.new_game()
		self.scene = 1
		gui.show_game_ui(self)


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

