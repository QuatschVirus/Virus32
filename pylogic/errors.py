from .base_components import *


class WidthMismatchException(Exception):
	def __init__(self, p1: Port | Bus, p2: Port | Bus):
		self.p1 = p1
		self.p2 = p2

	def __str__(self):
		return f"Width {self.p1.width} of {self.p1.__name__} does not match width {self.p2.width} of {self.p2.__name__}"
