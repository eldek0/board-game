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

UI_THEME_CONFIG = "sprites/design/ui_theme.json"

# Board token colors, one per player; the simulation allows up to 4 (letra: 2-4).
PLAYER_COLORS = (
	(50, 130, 255),   # jugador 1 azul
	(255, 190, 50),   # jugador 2 amarillo
	(80, 210, 120),   # jugador 3 verde
	(230, 90, 90),    # jugador 4 rojo
)

class App:
	btn_interactive: pygame_gui.elements.UIButton
	btn_simulation: pygame_gui.elements.UIButton

	input_player1: pygame_gui.elements.UITextEntryLine
	input_player2: pygame_gui.elements.UITextEntryLine

	btn_start: pygame_gui.elements.UIButton
	btn_roll: pygame_gui.elements.UIButton
	btn_reset: pygame_gui.elements.UIButton
	btn_new_sim: pygame_gui.elements.UIButton
	btn_menu: pygame_gui.elements.UIButton

	input_seed: pygame_gui.elements.UITextEntryLine
	input_players: pygame_gui.elements.UITextEntryLine
	btn_sim_start: pygame_gui.elements.UIButton

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
		self.sim_error = ""
		self.simulation_mode = False
		self.simulation_interval = 1200  # milisegundos entre turnos
		self.last_simulation_step = 0

		# Mouse
		self.mouse_control = Mouse()

		# DeltaTime variables
		self.prev_time, self.now_time = time.time(), time.time()

		# Scrolling background
		self.bg_offset = 0.0

		# Partida
		self.num_players = players
		self.seed = seed
		self.player_names = tuple(
			f"Player {i+1}" for i in range(self.num_players)
		)
		self.new_game()

		# Widgets
		self.ui_manager = pygame_gui.UIManager(self.dimentions, UI_THEME_CONFIG)
		gui.create_mode_ui(self)
		gui.create_name_ui(self)
		gui.create_sim_config_ui(self)
		gui.create_game_ui(self)

		gui.show_mode_ui(self)

	def new_game(self):
		self.game_state = GameState(
			players=tuple(
				Player(
					name=self.player_names[i],
					color=PLAYER_COLORS[i]
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
			self.bg_offset += gui.BG_SPEED * self.deltaTime

			self.game_events(events)

			gui.sync_console(self)
			self.ui_manager.update(self.deltaTime)

			self.update(events)

	def start_simulation_config(self):
		"""Opens the seed / player-count form; the simulation starts from there."""
		self.simulation_mode = False
		self.sim_error = ""
		self.scene = 3

		self.input_seed.set_text("")
		self.input_players.set_text(str(self.num_players))

		gui.show_sim_config_ui(self)

	def start_simulation_mode(self):
		"""Validates the config form and launches the simulation."""
		seed_text = self.input_seed.get_text().strip()
		players_text = self.input_players.get_text().strip()

		if seed_text and not seed_text.isdigit():
			self.sim_error = "La semilla debe ser un numero entero."
			return

		if not players_text.isdigit() or not (2 <= int(players_text) <= 4):
			self.sim_error = "La cantidad de jugadores debe estar entre 2 y 4."
			return

		self.sim_error = ""
		# An empty seed field means "surprise me", but we still pin the drawn value
		# so the run stays reproducible and can be reported back to the player.
		self.seed = int(seed_text) if seed_text else random.randint(0, 9999)
		self.num_players = int(players_text)
		self.player_names = tuple(
			f"Player {i+1}" for i in range(self.num_players)
		)

		self.simulation_mode = True
		self.restart_simulation()

		self.scene = 2
		gui.show_simulation_ui(self)

	def restart_simulation(self):
		"""Rebuilds the state and the log for a simulation run with the current seed."""
		self.new_game()

		game_log.clear()
		self.log_box.set_text("")
		game_log.log(f"Semilla: {self.seed} - Jugadores: {self.num_players}")

		self.last_simulation_step = pygame.time.get_ticks()

	def new_simulation(self):
		"""Runs another simulation, drawing a fresh seed."""
		self.seed = random.randint(0, 9999)
		self.restart_simulation()

	def game_events(self, events):
		for event in events:

			if event.type == QUIT:
				self.playing = False

			elif event.type == pygame.VIDEORESIZE:
				self.dimentions = (event.w, event.h)
				self.surface = pygame.display.set_mode(self.dimentions, pygame.RESIZABLE)
				self.ui_manager.set_window_resolution(self.dimentions)
				gui.layout_ui(self)

			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE and self.can_roll_with_key():
					self.roll_dice()

			elif event.type == pygame_gui.UI_BUTTON_PRESSED:
				if event.ui_element == self.btn_interactive:
					self.start_interactive_mode()

				elif event.ui_element == self.btn_simulation:
					self.start_simulation_config()

				elif event.ui_element == self.btn_sim_start:
					self.start_simulation_mode()

				elif event.ui_element == self.btn_start:
					self.start_interactive_game()

				elif event.ui_element == self.btn_roll:
					self.roll_dice()

				elif event.ui_element == self.btn_reset:
					self.reset_game()

				elif event.ui_element == self.btn_new_sim:
					self.new_simulation()

				elif event.ui_element == self.btn_menu:
					self.back_to_menu()

			self.ui_manager.process_events(event)

	def back_to_menu(self):
		"""Drops the running game and goes back to the mode selection screen."""
		self.simulation_mode = False
		self.scene = 0

		self.new_game()
		self.btn_roll.enable()

		game_log.clear()
		self.log_box.set_text("")

		gui.show_mode_ui(self)

	def start_interactive_mode(self):
		self.simulation_mode = False
		self.scene = 1
		gui.show_name_ui(self)

	def reset_game(self):
		"""Restarts the current game.

		An interactive restart draws a fresh seed, so the same two players get a
		different game each time. The simulation keeps its seed here, so a run can be
		watched again; "Nueva partida" is what changes it.
		"""
		if self.simulation_mode:
			self.restart_simulation()
			self.btn_roll.enable()
			return

		self.seed = random.randint(0, 9999)
		self.new_game()

		self.btn_roll.show()
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
		self.num_players = 2
		self.name_error = ""

		self.new_game()

		self.scene = 2
		gui.show_game_ui(self)


	def can_roll_with_key(self) -> bool:
		"""SPACE only rolls during an interactive game, never in the menus or the simulation."""
		return self.scene == 2 and not self.simulation_mode

	def roll_dice(self):
		if self.game_state.winner:
			return

		self.last_roll = self.game_state.rng.randint(1, 6)
		self.game_state = play_turn(self.game_state, self.last_roll)

		if self.game_state.winner:
			self.btn_roll.disable()

	def update(self, events):
		self.update_simulation()
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

