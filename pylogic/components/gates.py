from ..classes import State
from ..base_components import InputPort, OutputPort, Bus, TriggerPort, Port
from ..enums import BitState, Edge, BufferSetting
from ..errors import WidthMismatchException


class Not:
	def __init__(self, width: int):
		self.I = InputPort(width)
		self.I.set_callback(self.on_change)
		self.O = OutputPort(width)
		self.width = width
		self.state = State(width)

	def on_change(self, state: State, _):
		for i in range(self.width):
			if state.get(i) == BitState.FLOATING:
				self.state.set(i, BitState.ERROR)
			elif state.get(i) == BitState.ERROR:
				self.state.set(i, BitState.ERROR)
			elif state.get(i) == BitState.LOW:
				self.state.set(i, BitState.HIGH)
			elif state.get(i) == BitState.HIGH:
				self.state.set(i, BitState.LOW)
		self.O.set_state(self.state)


class Buffer:
	def __init__(self, width: int, setting: BufferSetting):
		self.I = InputPort(width)
		self.I.set_callback(self.on_change)
		self.O = OutputPort(width)
		self.width = width
		self.state = State(width)
		self.setting = setting

	def on_change(self, state: State, _):
		for i in range(self.width):
			if state.get(i) == BitState.FLOATING:
				self.state.set(i, BitState.FLOATING)
			elif state.get(i) == BitState.ERROR:
				self.state.set(i, BitState.ERROR)
			else:
				if self.setting == BufferSetting.LOW_HIGH:
					self.state.set(i, state.get(i))
				elif self.setting == BufferSetting.LOW_FLOATING:
					if state.get(i) == BitState.LOW:
						self.state.set(i, BitState.LOW)
					elif state.get(i) == BitState.HIGH:
						self.state.set(i, BitState.FLOATING)
				elif self.setting == BufferSetting.FLOATING_HIGH:
					if state.get(i) == BitState.LOW:
						self.state.set(i, BitState.FLOATING)
					elif state.get(i) == BitState.HIGH:
						self.state.set(i, BitState.HIGH)
		self.O.set_state(self.state)


class And:
	def __init__(self, width: int):
		self.width = width
		self.O = OutputPort(width)
		self.inputs: list[InputPort] = []
		self.state = State(width)

	def add_input(self):
		ip = InputPort(self.width)
		ip.set_callback(self.on_change)
		return ip

	def on_change(self, state: State, port: Port):
		for i in range(self.width):
			if all(p.state.get(i) == BitState.FLOATING or p.state.get(i) == BitState.ERROR for p in self.inputs):
				self.state.set(i, BitState.ERROR)
			elif all(p.state.get(i) == BitState.HIGH for p in self.inputs):
				self.state.set(i, BitState.HIGH)
			else:
				self.state.set(i, BitState.LOW)
		self.O.set_state(self.state)


class Or:
	def __init__(self, width: int):
		self.width = width
		self.O = OutputPort(width)
		self.inputs: list[InputPort] = []
		self.state = State(width)

	def add_input(self):
		ip = InputPort(self.width)
		ip.set_callback(self.on_change)
		return ip

	def on_change(self, state: State, port: Port):
		for i in range(self.width):
			if any(p.state.get(i) == BitState.FLOATING or p.state.get(i) == BitState.ERROR for p in self.inputs):
				self.state.set(i, BitState.ERROR)
			elif all(p.state.get(i) == BitState.LOW for p in self.inputs):
				self.state.set(i, BitState.LOW)
			else:
				self.state.set(i, BitState.HIGH)
		self.O.set_state(self.state)


class Nand:
	def __init__(self, width: int):
		self.width = width
		self.O = OutputPort(width)
		self.inputs: list[InputPort] = []
		self.state = State(width)

	def add_input(self):
		ip = InputPort(self.width)
		ip.set_callback(self.on_change)
		return ip

	def on_change(self, state: State, port: Port):
		for i in range(self.width):
			if all(p.state.get(i) == BitState.FLOATING or p.state.get(i) == BitState.ERROR for p in self.inputs):
				self.state.set(i, BitState.ERROR)
			elif all(p.state.get(i) == BitState.HIGH for p in self.inputs):
				self.state.set(i, BitState.LOW)
			else:
				self.state.set(i, BitState.HIGH)
		self.O.set_state(self.state)


class Nor:
	def __init__(self, width: int):
		self.width = width
		self.O = OutputPort(width)
		self.inputs: list[InputPort] = []
		self.state = State(width)

	def add_input(self):
		ip = InputPort(self.width)
		ip.set_callback(self.on_change)
		return ip

	def on_change(self, state: State, port: Port):
		for i in range(self.width):
			if any(p.state.get(i) == BitState.FLOATING or p.state.get(i) == BitState.ERROR for p in self.inputs):
				self.state.set(i, BitState.ERROR)
			elif all(p.state.get(i) == BitState.LOW for p in self.inputs):
				self.state.set(i, BitState.HIGH)
			else:
				self.state.set(i, BitState.LOW)
		self.O.set_state(self.state)


class Xor:
	def __init__(self, width: int):
		self.width = width
		self.O = OutputPort(width)
		self.inputs: list[InputPort] = []
		self.state = State(width)

	def add_input(self):
		ip = InputPort(self.width)
		ip.set_callback(self.on_change)
		return ip

	def on_change(self, state: State, port: Port):
		for i in range(self.width):
			if any(p.state.get(i) == BitState.FLOATING or p.state.get(i) == BitState.ERROR for p in self.inputs):
				self.state.set(i, BitState.ERROR)
			elif [p.state.get(i) for p in self.inputs].count(BitState.HIGH) == 1:
				self.state.set(i, BitState.HIGH)
			else:
				self.state.set(i, BitState.LOW)
		self.O.set_state(self.state)


class Xor:
	def __init__(self, width: int):
		self.width = width
		self.O = OutputPort(width)
		self.inputs: list[InputPort] = []
		self.state = State(width)

	def add_input(self):
		ip = InputPort(self.width)
		ip.set_callback(self.on_change)
		return ip

	def on_change(self, state: State, port: Port):
		for i in range(self.width):
			if any(p.state.get(i) == BitState.FLOATING or p.state.get(i) == BitState.ERROR for p in self.inputs):
				self.state.set(i, BitState.ERROR)
			elif [p.state.get(i) for p in self.inputs].count(BitState.HIGH) == 1:
				self.state.set(i, BitState.LOW)
			else:
				self.state.set(i, BitState.HIGH)
		self.O.set_state(self.state)


class ControlledBuffer:
	def __init__(self, width: int):
		self.width = width
		self.state = State(width)
		self.I = InputPort(width)
		self.E = InputPort(1)
		self.O = OutputPort(width)
		self.I.set_callback(self.on_change)
		self.E.set_callback(self.on_e_change)

	def on_change(self, state: State, _):
		for i in range(self.width):
			if state.get(i) == BitState.FLOATING or state.get(i) == BitState.ERROR:
				self.state.set(i, BitState.ERROR)
			else:
				self.state.set(i, state.get(i))
		if self.E.state.get(0) == BitState.HIGH:
			self.O.set_state(self.state)

	def on_e_change(self, state: State, _):
		if state.get(0) == BitState.HIGH:
			self.O.set_state(self.state)
		elif state.get(0) == BitState.LOW:
			self.O.set_state(State(self.width))
		else:
			self.O.set_state(State(self.width, starter=BitState.ERROR))
