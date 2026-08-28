# Animation engine 2.0: Made by Eduardo Delfante

from dataclasses import dataclass

@dataclass
class AnimationState:
	value: float          # Current value, moves towards the limit
	limit: float          # Target value
	add_value: float      # Magnitude to move per unit of time (0 pauses the animation)
	force_when_reached: bool = False  # Pin the value to the limit once it has been reached
	times_limit_reached: int = 0      # How many times the limit was reached

class Animation:
	def __init__(self, verbose=False):
		self.Animations = {} # {animation_name: AnimationState}
		self.verbose = verbose

	def _log(self, message):
		if self.verbose:
			print(message)

	def new_animation(self, animation_name, initial_value, limit, add_value=1, force_when_reached=False):
		# Create a new animation or overwrite one
		if animation_name in self.Animations:
			self._log(animation_name + " was overwritten.")
		else:
			self._log(animation_name + " created.")

		# The direction comes from the sign of (limit - value), so add_value is a magnitude
		self.Animations[animation_name] = AnimationState(
			value=initial_value,
			limit=limit,
			add_value=abs(add_value),
			force_when_reached=force_when_reached,
		)

	def delete_animation(self, animation_name):
		self.Animations.pop(animation_name, None)

	def update(self, deltaTime=1, exceptions=()):
		skip = frozenset(exceptions)

		for animation_name, animation in list(self.Animations.items()):

			if animation_name in skip:
				continue

			if animation.add_value == 0: # Paused
				continue

			# Already reached: hold the value there without counting it again
			if animation.force_when_reached and animation.times_limit_reached > 0:
				animation.value = animation.limit
				continue

			distance = animation.limit - animation.value

			if distance == 0:
				continue

			step = animation.add_value * deltaTime

			if step >= abs(distance): # The step reaches or overshoots the limit
				animation.value = animation.limit
				animation.times_limit_reached += 1
			elif distance > 0:
				animation.value += step # The limit is ahead, it ADDS
			else:
				animation.value -= step # The limit is behind, it SUBSTRACTS

	# Getters
	def get_value(self, animation_name):
		return self.Animations[animation_name].value

	def get_limit(self, animation_name):
		return self.Animations[animation_name].limit

	def get_valueToAdd(self, animation_name):
		return self.Animations[animation_name].add_value

	def get_force_when_reached(self, animation_name):
		return self.Animations[animation_name].force_when_reached

	def get_times_limit_reached(self, animation_name):
		return self.Animations[animation_name].times_limit_reached

	def get_Animations(self):
		return self.Animations

	def get_animation(self, animation_name):
		return self.Animations.get(animation_name) # None if it does not exist

	# Setters
	def set_value(self, animation_name, value):
		self.Animations[animation_name].value = value

	def set_limit(self, animation_name, limit, reset_limit_counter=False):
		self.Animations[animation_name].limit = limit
		if reset_limit_counter:
			self.reset_limit_counter(animation_name)

	def set_valueToAdd(self, animation_name, value_to_add):
		self.Animations[animation_name].add_value = abs(value_to_add)

	def set_force_when_reached(self, animation_name, force_when_reached):
		self.Animations[animation_name].force_when_reached = force_when_reached

	def reset_limit_counter(self, animation_name):
		self.Animations[animation_name].times_limit_reached = 0


if __name__ == "__main__":
	Animation_handler = Animation(verbose=True)

	# Creates two new animations
	Animation_handler.new_animation("Cow", 0, 10, 1)

	Animation_handler.new_animation("Ball", 0, -25, 1)

	# Delete an animation
	Animation_handler.delete_animation("Ball")

	# Updates the animations
	for i in range(9):
		Animation_handler.update()

	# Prints the animation
	print(Animation_handler.get_value("Cow"))

	Animation_handler.new_animation("Cow", 0, 10, 1) # If the animation already exsists it overwrites it

	print(Animation_handler.get_value("Cow"))
