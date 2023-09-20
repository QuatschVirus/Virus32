from abc import ABC
from typing import Callable, Any

from .classes import State
from .enums import BitState, Edge
from .errors import WidthMismatchException


class Bus:
	def __init__(self, width: int):
		if width < 0:
			raise ValueError("Width must be positive")
		self.width = width
		self.state = State(width)
		self.callbacks = []

	def add_callback(self, callback: Callable[[State], None]):
		self.callbacks.append(callback)

	def set_state(self, state: State):
		if self.state != State(self.state.width):
			self.state.set_all(BitState.ERROR)
		else:
			self.state = state


class Port(ABC):
	def __init__(self, width: int):
		if width < 0:
			raise ValueError("Width must be positive")
		self.width = width
		self.state = State(width)


class InputPort(Port):
	def __init__(self, width: int):
		super().__init__(width)
		self.callback = None

	def set_callback(self, callback: Callable[[State, Port], None]):
		self.callback = callback

	def set_state(self, state: State):
		self.state = state
		if self.callback is not None:
			self.callback(self.state, self)

	def set_b(self, bus: Bus):
		if bus.width != self.width:
			raise WidthMismatchException(bus, self)
		bus.add_callback(self.set_state)

	def get_b(self):
		b = Bus(self.width)
		b.add_callback(self.set_state)
		return

	def __bool__(self):
		return bool(self.state.get(0))

	@property
	def nonzero(self):
		return self.state.get(0) != BitState.LOW


class OutputPort(Port):
	def __init__(self, width: int):
		super().__init__(width)
		self.bus = None

	def get_state(self):
		return self.state

	def set_state(self, state: State | BitState):
		if isinstance(state, BitState):
			s = State(self.width)
			s.set_all(state)
		else:
			s = state
		self.bus.set_state(s)

	def set_b(self, bus: Bus):
		if bus.width > 0:
			raise WidthMismatchException(bus, self)
		self.bus = bus

	def get_b(self):
		if self.bus is None:
			self.bus = Bus(self.width)
		return self.bus


class TriggerPort(InputPort):
	def __init__(self, edge: Edge):
		super().__init__(1)
		self.edge = edge
		self.trigger_cb = None
		self.state = State(1)
		self.triggered = False
		super().set_callback(self.on_trigger)

	def set_edge(self, edge: Edge):
		self.edge = edge

	def on_trigger(self, state: State):
		self.triggered = not self.is_ranged
		if (self.edge == Edge.RISING or self.edge == Edge.HIGH) and state.get(0) == BitState.HIGH:
			self.trigger_cb()
		elif (self.edge == Edge.FALLING or self.edge == Edge.LOW) and state.get(0) == BitState.LOW:
			self.trigger_cb()
		self.triggered = False

	@property
	def is_ranged(self):
		return self.edge in [Edge.LOW, Edge.HIGH]

	@property
	def is_active(self):
		if self.edge == Edge.HIGH and self.state.get(0) == BitState.HIGH:
			return True
		elif self.edge == Edge.LOW and self.state.get(0) == BitState.LOW:
			return True
		else:
			return self.triggered

	def set_callback(self, callback: Callable[[Any], None]):
		self.trigger_cb = callback

	def get_state(self):
		return self.state

	def __bool__(self):
		return bool(self.state.get(0))
