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
	btn_interactive: pygame_gui.elements.UIButton
	btn_simulation: pygame_gui.elements.UIButton

	input_player1: pygame_gui.elements.UITextEntryLine
	input_player2: pygame_gui.elements.UITextEntryLine

	btn_start: pygame_gui.elements.UIButton
	btn_roll: pygame_gui.elements.UIButton
	btn_reset: pygame_gui.elements.UIButton

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
		self.simulation_mode = False
		self.simulation_interval = 1200  # milisegundos entre turnos
		self.last_simulation_step = 0

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
		gui.create_mode_ui(self)
		gui.create_name_ui(self)
		gui.create_game_ui(self)

		gui.show_mode_ui(self)

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

	def start_simulation_mode(self):
		self.simulation_mode = True

		self.player_names = (
		"Player 1",
		"Player 2"
		)

		self.new_game()

		self.scene = 2
		self.last_simulation_step = pygame.time.get_ticks()

		gui.show_simulation_ui(self)

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
				if event.ui_element == self.btn_interactive:
					self.start_interactive_mode()

				elif event.ui_element == self.btn_simulation:
					self.start_simulation_mode()

				elif event.ui_element == self.btn_start:
					self.start_interactive_game()

				elif event.ui_element == self.btn_roll:
					self.roll_dice()

				elif event.ui_element == self.btn_reset:
					self.reset_game()

			self.ui_manager.process_events(event)

	def start_interactive_mode(self):
		self.simulation_mode = False
		self.scene = 1
		gui.show_name_ui(self)

	def layout_ui(app: App):
		width, height = app.surface.get_size()
		app.btn_interactive.set_relative_position(
			(
				width // 2 - gui.BTN_W // 2,
				height // 2  - 30
			)
		)

		app.btn_simulation.set_relative_position(
			(
				width // 2 - gui.BTN_W // 2,
				height // 2 + 30
			)
		)

		input1_rect, input2_rect, start_rect = gui.name_ui_rects(
			width,
			height
		)

		app.input_player1.set_relative_position(input1_rect.topleft)
		app.input_player2.set_relative_position(input2_rect.topleft)
		app.btn_start.set_relative_position(start_rect.topleft)

		gui.layout_game_ui(app)

	def reset_game(self):
		self.new_game()
		if self.simulation_mode:
			self.last_simulation_step = pygame.time.get_ticks()
			self.btn_roll.enable()

		else: 
			self.btn_roll.show()
			self.btn_roll.enable()
			
		game_log.clear()
		self.log_box.set_text("")

	def start_interactive_mode(self):
		self.scene = 1
		gui.show_name_ui(self)


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

		self.scene = 2
		gui.show_game_ui(self)


	def roll_dice(self):
		if self.game_state.winner:
			return

		self.last_roll = self.game_state.rng.randint(1, 6)
		self.game_state = play_turn(self.game_state, self.last_roll)

		if self.game_state.winner:
			self.btn_roll.disable()

	def update(self, events):
		self.update_simulation()
		self.surface.fill((105,105,105))

		# Draw on screen
		dr.Draw(self)
		self.ui_manager.draw_ui(self.surface)

		# Update each frame
		pygame.display.update()

	def update_simulation(self):
		if not self.simulation_mode:
			return

		if self.game_state.winner:
			return

		current_time = pygame.time.get_ticks()

		if current_time - self.last_simulation_step < self.simulation_interval:
			return

		self.last_simulation_step = current_time

		self.last_roll = self.game_state.rng.randint(1, 6)

		self.game_state = play_turn(
			self.game_state,
			self.last_roll
	)

