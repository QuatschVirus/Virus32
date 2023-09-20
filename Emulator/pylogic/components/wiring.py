import time

from ..classes import State
from ..base_components import InputPort, OutputPort, Bus, TriggerPort, Port
from ..enums import BitState, Edge
from ..errors import WidthMismatchException


class Splitter:
	def __init__(self, width: int):
		self.width = width
		self.state = State(width)
		self.inputs: dict[InputPort, list[int]] = {}
		self.outputs: dict[list[int], OutputPort] = {}

	def add_output(self, indices: list[int]):
		self.outputs[indices] = OutputPort(len(indices))
		return self.outputs[indices]

	def get_output(self, index: int):
		for k, v in self.outputs.items():
			if index in k:
				return v

	def add_input(self, indices: list[int]):
		ip = InputPort(len(indices))
		self.inputs[ip] = indices
		ip.set_callback(self.on_input_change)
		return ip

	def on_input_change(self, state: State, ip: Port):
		if not isinstance(ip, InputPort):
			raise TypeError(type(ip))
		indices = self.inputs[ip]
		for i in range(len(indices)):
			self.state.set(indices[i], state.get(i))
		for k, v in self.outputs.items():
			s = State(len(k))
			for i in range(len(k)):
				s.set(i, self.state.get(k[i]))
			v.set_state(s)


class PullResistor:
	def __init__(self, width: int, setting: BitState):
		self.width = width
		self.setting = setting
		self._I = InputPort(width)
		self._I.set_callback(self.on_input_change)
		self._O = OutputPort(width)

	def on_input_change(self, state):
		n_state = State(self.width)
		if self.setting == BitState.FLOATING:
			n_state = state
		elif self.setting == BitState.ERROR:
			n_state.set_all(BitState.ERROR)
		else:
			for i in range(self.width):
				if state.get(i) == BitState.FLOATING:
					n_state.set(i, self.setting)
		self._O.set_state(n_state)

	def set_b(self, bus: Bus):
		if bus.width > self.width:
			raise WidthMismatchException(bus, self._O)
		self._I.set_b(bus)
		self._O.set_b(bus)


class Clock:
	def __init__(self, frequency: int):
		super().__init__()
		self.frequency = frequency
		self.running = True
		self.T = TriggerPort(Edge.RISING)
		self.I = TriggerPort(Edge.RISING)
		self.T.set_callback(self.start)
		self.I.set_callback(self.stop)
		self.C = OutputPort(1)

	def start(self):
		while self.running:
			self.C.set_state(BitState.HIGH)
			time.sleep(1 / (self.frequency / 2))
			self.C.set_state(BitState.LOW)
			time.sleep(1 / (self.frequency / 2))

	def stop(self):
		self.running = False


class Constant:
	def __init__(self, width: int, value: State | BitState | int):
		self.width = width
		self.state = State(width)
		if isinstance(value, int):
			self.state.from_int(value)
		elif isinstance(value, BitState):
			self.state.set_all(value)
		else:
			self.state = value
		self.O = OutputPort(width)

	def set_b(self, bus: Bus):
		self.O.set_b(bus)
		self.push()

	def push(self):
		self.O.set_state(self.state)


class Readout:
	def __init__(self, width: int, name=__name__):
		self.width = width
		self.I = InputPort(width)
		self.I.set_callback(self.on_input_change)
		self.name = name

	def on_input_change(self, state: State):
		print(f"{self.name}: {state}")