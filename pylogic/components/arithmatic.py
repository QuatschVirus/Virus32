from ..classes import State
from ..base_components import InputPort, OutputPort, Bus, TriggerPort, Port
from ..enums import BitState, Edge, BufferSetting
import math
from ..errors import WidthMismatchException


class ALU:
	def __init__(self, width: int):
		self.width = width
		self.IA = InputPort(width)
		self.IB = InputPort(width)
		self.IC = InputPort(width)
		self.OA = OutputPort(width)
		self.OB = OutputPort(width)
		self.M = InputPort(1)

		self.IA.set_callback(self.on_change)
		self.IB.set_callback(self.on_change)
		self.IC.set_callback(self.on_change)

	def on_change(self, state: State, port: Port):
		mode = int(self.M.state)
		if mode == 0:  # Addition
			o = int(self.IA.state) + int(self.IB.state) + (1 if self.IC.state.get(0) == BitState.HIGH else 0)
			if o > 2**(self.width / 2) - 1:
				o -= 2**(self.width / 2) - 1
				self.OB.state.set(0, BitState.HIGH)
			else:
				self.OB.state.set(0, BitState.LOW)
			self.OA.set_state(State(self.width).from_int(o))
			self.OB.set_state(self.OB.state)
		elif mode == 1:  # Subtraction
			o = int(self.IA.state) - int(self.IB.state) - (1 if self.IC.state.get(0) == BitState.HIGH else 0)
			if o < -(2**(self.width / 2)):
				o += 2**(self.width / 2)
				self.OB.state.set(0, BitState.HIGH)
			else:
				self.OB.state.set(0, BitState.LOW)
			self.OA.set_state(State(self.width).from_int(o))
			self.OB.set_state(self.OB.state)
		else:
			print("Mode not (yet) supported/implemented.")
