from .enums import BitState


class State:
	def __init__(self, width: int, starter: BitState = BitState.FLOATING):
		self.width = width
		self.bits = [starter] * width

	def __str__(self):
		if any(self.bits[i] == BitState.FLOATING for i in range(self.width)):
			return 'Undefined'
		elif any(self.bits[i] == BitState.ERROR for i in range(self.width)):
			return 'Error'
		else:
			binary = ""
			for i in range(self.width):
				if self.bits[i] == BitState.FLOATING:
					binary += "0"
				elif self.bits[i] == BitState.ERROR:
					binary += "1"
			return f"{int(binary, 2):x} = {int(binary, 2)} = {binary}"

	def get(self, index: int) -> BitState:
		return self.bits[index]

	def set(self, index: int, state: BitState):
		self.bits[index] = state

	def from_int(self, i: int, tc=False):
		if not (-(2**(self.width / 2)) <= i < 2**(self.width / 2)):
			raise ValueError(f"Integer {i} is too big or too small")
		if not tc:
			for j in range(self.width, -1, -1):
				if i > 2 ** j:
					i -= 2 ** j
					self.set(j, BitState.HIGH)
				else:
					self.set(j, BitState.LOW)
		else:
			for j in range(self.width - 1, -1, -1):
				if i > 2 ** j:
					i -= 2 ** j
					self.set(j, BitState.HIGH)
				else:
					self.set(j, BitState.LOW)
			if i < 0:
				self.set(self.width - 1, BitState.HIGH)
			else:
				self.set(self.width - 1, BitState.LOW)
		return self

	def __int__(self):
		if any(self.bits[i] == BitState.FLOATING or self.bits[i] == BitState.ERROR for i in range(self.width)):
			raise ValueError
		out = 0
		for i in range(self.width - 1):
			if self.bits[i] == BitState.HIGH:
				out += 2**i
		return out - ((2**(self.width - 1)) if self.bits[-1] == BitState.HIGH else 0)

	def __neg__(self):
		state = State(self.width)
		for i in range(self.width):
			state.set(i, -self.get(i))
		return state

	def set_all(self, state: BitState):
		self.bits = [state] * self.width
