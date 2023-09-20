from pylogic.components.memory import *


class StateRegister:
	def __init__(self):
		self.D = InputPort(20)
		self.S = InputPort(5)

		self.R = TriggerPort(Edge.HIGH)
		self.C = TriggerPort(Edge.FALLING)

		self.Q = OutputPort(20)

		self.states = [State(20, starter=BitState.LOW)] * 5
