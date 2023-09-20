from abc import ABC
from operator import xor
from typing import Callable
import math

from ..util import *
from ..classes import State
from ..base_components import InputPort, OutputPort, Bus, TriggerPort, Port
from ..enums import BitState, Edge, BufferSetting, OverflowSetting
from ..errors import WidthMismatchException


class FlipFlop(ABC):
	def __init__(self, clock_edge: Edge):
		self.state = State(1, starter=BitState.LOW)
		self.Q = OutputPort(1)
		self.Qi = OutputPort(1)
		self.S = TriggerPort(Edge.HIGH)
		self.R = TriggerPort(Edge.HIGH)
		self.C = TriggerPort(clock_edge)
		self.change_cb: Callable[[None], BitState] = lambda: BitState.FLOATING
		self.S.set_callback(self.on_change)
		self.R.set_callback(self.on_change)

	def set_change_callback(self, callback: Callable[[None], BitState]):
		self.change_cb = callback

	def on_change(self, state: State, port: Port):
		if self.R:
			self.state.set(0, BitState.LOW)
		if self.C.is_active():
			if self.S:
				self.state.set(0, BitState.HIGH)
			else:
				self.state.set(0, self.change_cb())
			self.Q.set_state(self.state)
			self.Qi.set_state(-self.state)


class DFlipFlop(FlipFlop):
	def __init__(self, clock_edge: Edge):
		super().__init__(clock_edge)
		self.D = InputPort(1)
		self.D.set_callback(self.on_change)
		self.set_change_callback(self.change)

	def change(self):
		return self.D.state.get(0)


class TFlipFlop(FlipFlop):
	def __init__(self, clock_edge: Edge):
		super().__init__(clock_edge)
		self.T = InputPort(1)
		self.T.set_callback(self.on_change)
		self.set_change_callback(self.change)

	def change(self):
		if self.T.state.get(0):
			return -self.state.get(0)


class JKFlipFlop(FlipFlop):
	def __init__(self, clock_edge: Edge):
		super().__init__(clock_edge)
		self.J = InputPort(1)
		self.K = InputPort(1)
		self.J.set_callback(self.on_change)
		self.K.set_callback(self.on_change)
		self.set_change_callback(self.change)

	def change(self):
		if self.J.state.get(0) and self.K.state.get(0):
			return -self.state.get(0)
		elif self.J.state.get(0):
			return BitState.HIGH
		elif self.J.state.get(0):
			return BitState.LOW


class SRFlipFlop(FlipFlop):
	def __init__(self, clock_edge: Edge):
		super().__init__(clock_edge)
		self.S = InputPort(1)
		self.R = InputPort(1)
		self.S.set_callback(self.on_change)
		self.R.set_callback(self.on_change)
		self.set_change_callback(self.change)

	def change(self):
		if self.S.state.get(0):
			return BitState.LOW
		elif self.S.state.get(0):
			return BitState.HIGH


class Register:
	def __init__(self, width: int, clock_edge: Edge):
		self.width = width
		self.D = InputPort(width)
		self.WE = TriggerPort(Edge.HIGH)
		self.OE = TriggerPort(Edge.HIGH)
		self.R = TriggerPort(Edge.HIGH)
		self.Q = OutputPort(width)
		self.C = TriggerPort(clock_edge)

		self.state = State(width, starter=BitState.LOW)

		self.D.set_callback(self.on_change)
		self.WE.set_callback(self.on_change)
		self.OE.set_callback(self.on_change)
		self.R.set_callback(self.on_change)
		self.Q.set_state(self.state)

	def on_change(self):
		if self.R:
			self.state = State(self.width, starter=BitState.LOW)
		if self.C.is_active():
			if self.WE:
				self.state = self.D.state
		if self.OE:
			self.Q.set_state(self.state)
		else:
			self.Q.set_state(State(self.width, starter=BitState.LOW))


class Counter:
	def __init__(
			self,
			width: int,
			max_value: int | None = None,
			overflow_setting: OverflowSetting = OverflowSetting.WRAP,
			clock_edge: Edge = Edge.RISING
	):
		self.width = width
		self.max_value = max_value if max_value is not None else (2 ** width) - 1
		self.overflow_setting = overflow_setting
		if clock_edge in [Edge.HIGH, Edge.LOW]:
			raise ValueError("Counter does not accept continuos edges")

		self.state = State(width, starter=BitState.LOW)

		self.R = TriggerPort(Edge.HIGH)
		self.MS = TriggerPort(Edge.HIGH)
		self.DS = TriggerPort(Edge.HIGH)
		self.CE = TriggerPort(Edge.HIGH)
		self.C = TriggerPort(clock_edge)
		self.D = InputPort(width)

		self.R.set_callback(self.on_change)
		self.MS.set_callback(self.on_change)
		self.DS.set_callback(self.on_change)
		self.CE.set_callback(self.on_change)
		self.C.set_callback(self.on_change)
		self.D.set_callback(self.on_change)

		self.OF = OutputPort(1)
		self.O = OutputPort(width)

	def on_change(self, state: State, port: Port):
		if self.R:
			self.state = State(self.width, starter=BitState.LOW)
		elif (not self.C) and self.MS:
			self.state = self.D.state
		elif self.C.is_active() and not self.MS:
			new_int = int(self.state) + (1 if self.DS else -1)

			if (self.DS and new_int > self.max_value) or ((not self.DS) and new_int < 0):
				upper_end = new_int > self.max_value
				if self.overflow_setting == OverflowSetting.WRAP:
					self.state = State(self.width).from_int(0 if upper_end else self.max_value)
				elif self.overflow_setting == OverflowSetting.STAY:
					return
				elif self.overflow_setting == OverflowSetting.LOAD:
					self.state = self.D.state
				else:
					if new_int > (2 ** self.width) - 1:
						new_int = 0
			else:
				self.state = State(self.width).from_int(new_int)
			self.O.set_state(self.state)

			if (self.DS and new_int == self.max_value) or ((not self.DS) and new_int == 0):
				self.OF.set_state(BitState.HIGH)
			else:
				self.OF.set_state(BitState.LOW)


class ShiftRegister:
	def __init__(
			self,
			width: int,
			stages: int,
			edge: Edge
	):
		self.width = width
		self.stage_count = stages

		if edge in [Edge.HIGH, Edge.LOW]:
			raise ValueError("Counter does not accept continuos edges")

		self.R = TriggerPort(Edge.HIGH)
		self.L = InputPort(1)
		self.S = InputPort(1)
		self.C = TriggerPort(edge)

		self.S_IN = InputPort(width)

		self.inputs: list[InputPort] = [InputPort(width) for _ in range(stages)]
		self.outputs: list[OutputPort] = [OutputPort(width) for _ in range(stages)]

		self.stages: list[State] = [State(width, starter=BitState.LOW) for _ in range(stages)]

		self.R.set_callback(self.on_change)
		self.C.set_callback(self.on_change)

	def on_change(self, state: State, port: Port):
		if self.R:
			self.stages: list[State] = [State(self.width, starter=BitState.LOW) for _ in range(self.stage_count)]
		elif self.C.is_active:
			if self.L:
				for i in range(self.stage_count):
					self.stages[i] = self.inputs[i].state
			elif self.S.nonzero:
				temp: list[State] = [self.S_IN.state]
				temp.extend(self.stages)
				for i in range(self.stage_count - 1, -1, -1):
					self.stages[i] = temp[i]
		for i in range(self.stage_count):
			self.outputs[i].set_state(self.stages[i])

# Random generator left out, maybe later


class RAM:
	def __init__(
			self,
			addr_width: int,
			data_width: int,
			volatile: bool = True,
			edge: Edge = Edge.RISING,
			async_read: bool = False,
	):
		self.addr_width = addr_width
		self.data_width = data_width
		self.async_read = async_read

		self.R = TriggerPort(Edge.HIGH)
		self.A = InputPort(addr_width)
		self.WE = TriggerPort(Edge.HIGH)
		self.OE = TriggerPort(Edge.HIGH)
		self.C = TriggerPort(edge)

		self.IN = InputPort(data_width)
		self.OUT = OutputPort(data_width)

		self.locs: list[State] = [State(data_width, starter=BitState.LOW) for _ in range(2**addr_width)]

		if not volatile:
			dump = fetch_ram_dump(self.__name__)
			self.locs = [State(data_width).from_int(point) for point in dump]

		self.R.set_callback(self.on_change)
		self.A.set_callback(self.on_change)
		self.WE.set_callback(self.on_change)
		self.OE.set_callback(self.on_change)
		self.C.set_callback(self.on_change)
		self.IN.set_callback(self.on_change)

	def on_change(self, state: State, port: Port):
		if self.R:
			self.locs: list[State] = [State(self.data_width, starter=BitState.LOW) for _ in range(2**self.addr_width)]
		else:
			if (self.async_read or self.C.is_active) and self.OE:
				self.OUT.set_state(self.locs[int(self.A.state)])
			if self.WE and self.C.is_active:
				self.locs[int(self.A.state)] = self.IN.state
		update_ram_dump(self.__name__, [int(point) for point in self.locs])


class ROM:
	def __init__(
			self,
			addr_width: int,
			data_width: int,
			start_data_path: str = None
	):
		self.addr_width = addr_width
		self.data_width = data_width

		self.A = InputPort(addr_width)
		self.OE = TriggerPort(Edge.HIGH)
		self.O = OutputPort(data_width)

		if start_data_path is None:
			self.locs: list[State] = [State(data_width, starter=BitState.LOW) for _ in range(2 ** addr_width)]
		else:
			with open(start_data_path) as f:
				data = json.load(f)
			self.locs: list[State] = [State(data_width).from_int(point) for point in data]

	def on_change(self, state: State, port: Port):
		if self.OE:
			self.O.set_state(self.locs[int(self.A.state)])
