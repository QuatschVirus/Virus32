from pylogic.components.memory import *

# Busses
d_bus = Bus(32)
a_bus = Bus(32)

# Registers
dep_reg = Register(32, Edge.FALLING)
a_reg = Register(32, Edge.FALLING)
b_reg = Register(32, Edge.FALLING)
c_reg = Register(32, Edge.FALLING)
d_reg = Register(32, Edge.FALLING)

ramaddr_reg = Register(32, Edge.FALLING)

alua_reg = Register(32, Edge.RISING)
alub_reg = Register(32, Edge.RISING)
aluc_reg = Register(32, Edge.RISING)
aluoa_reg = Register(32, Edge.FALLING)
aluob_reg = Register(32, Edge.FALLING)

inst_reg = Register(32, Edge.FALLING)

