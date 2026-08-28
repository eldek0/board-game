import pygame

class Mouse:
	def __init__(self):
		self.mouse_button = pygame.mouse.get_pressed()
		self.mouse_hitbox = pygame.Rect((0,0), (1,1))

	def mouse_update(self):
		# Update Mouse's hitbox
		self.mouse_hitbox.left, self.mouse_hitbox.top = pygame.mouse.get_pos()

		# Update mouse button
		self.mouse_button = pygame.mouse.get_pressed()

	def mouse_press_action(self, index, action):
		if self.mouse_button[index] == 1: # Is being pressed
			action()
				
	def mouse_press_while_colliderecting(self, index, rect_to_colli, action):
		if self.mouse_hitbox.colliderect(rect_to_colli):
			self.mouse_press_action(index, action)