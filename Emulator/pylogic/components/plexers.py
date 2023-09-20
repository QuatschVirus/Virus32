from ..classes import State
from ..base_components import InputPort, OutputPort, Bus, TriggerPort, Port
from ..enums import BitState, Edge, BufferSetting
import math
from ..errors import WidthMismatchException


class Multiplexer:
	def __init__(self, width: int, selector_width: int):
		self.width = width
		self.state = State(width)
		self.selector_width = selector_width
		self.S = InputPort(selector_width)
		self.inputs = []
		for _ in range(2**selector_width):
			ip = InputPort(width)
			ip.set_callback(self.on_input_change)
			self.inputs.append(ip)
		self.O = OutputPort(width)

	def on_input_change(self, _, __):
		self.on_change(self.S.state, self.S)

	def on_change(self, state: State, _):
		if any(state.get(i) == BitState.FLOATING for i in range(self.width)):
			self.O.set_state(State(self.width))
		elif any(state.get(i) == BitState.ERROR for i in range(self.width)):
			self.O.set_state(State(self.width, starter=BitState.ERROR))
		else:
			self.O.set_state(self.inputs[int(state)].state)


class Demultiplexer:
	def __init__(self, width: int, selector_width: int, threestate=False):
		self.width = width
		self.state = State(width)
		self.selector_width = selector_width
		self.S = InputPort(selector_width)
		self.outputs = [OutputPort(self.width) for _ in range(2**selector_width)]
		self.I = InputPort(width)
		self.I.set_callback(self.on_input_change)
		self.threestate = threestate

	def on_input_change(self, _, __):
		self.on_change(self.S.state, self.S)

	def on_change(self, state: State, _):
		for i in range(self.width):
			p = self.outputs[i]
			if any(state.get(i) == BitState.FLOATING for i in range(self.width)):
				p.set_state(State(self.width))
			elif any(state.get(i) == BitState.ERROR for i in range(self.width)):
				p.set_state(State(self.width, starter=BitState.ERROR))
			elif i == int(state):
				p.set_state(self.I.state)
			else:
				p.set_state(State(self.width, starter=BitState.FLOATING if self.threestate else BitState.LOW))


class BitSelector:
	def __init__(self, i_width: int, o_width: int):
		self.i_width = i_width
		self.o_width = o_width
		if self.i_width < self.o_width:
			raise ValueError
		self.I = InputPort(i_width)
		self.I.set_callback(self.on_input_change)
		self.O = OutputPort(o_width)
		self.S = InputPort(math.ceil(math.log(i_width / o_width, 2)))
		self.S.set_callback(self.on_change)

	def on_input_change(self, _, __):
		self.on_change(self.S.state, self.S)

	def on_change(self, state: State, _):
		if int(state) > (self.i_width / self.o_width):
			raise ValueError
		start_i = int(state) * self.o_width
		end_i = start_i + self.o_width
		s = State(self.o_width)
		s.bits = self.I.state.bits[start_i:end_i]
