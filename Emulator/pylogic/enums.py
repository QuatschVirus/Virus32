from enum import Enum


class BitState(Enum):
	FLOATING = 0
	LOW = 1
	HIGH = 2
	ERROR = 3

	def __neg__(self):
		if self.LOW:
			return self.HIGH
		elif self.HIGH:
			return self.LOW
		else:
			return self.ERROR

	def __bool__(self):
		if self.LOW:
			return False
		elif self.HIGH:
			return True
		else:
			raise ValueError("Floating and Error values cannot be cast into boolean")


class Edge(Enum):
	RISING = 0
	FALLING = 1
	LOW = 2
	HIGH = 3


class BufferSetting(Enum):
	LOW_HIGH = 0
	LOW_FLOATING = 1
	FLOATING_HIGH = 2


class OverflowSetting(Enum):
	WRAP = 0
	STAY = 1
	CONTINUE = 2
	LOAD = 3
