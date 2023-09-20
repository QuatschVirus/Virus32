import re
import sys
import os

ARG_REGEX = re.compile(r"-f (\d+)|-l ([a-zA-Z0-9/]+\.axs)|(-d)")

AXS_REGEX = re.compile(r"// ([A-Z]{2,5})\n((?:(?:EIS|DWE|DOE|AWE|AOE|ALU|GPU|ITR)(?: A(?: [AB])?| \d{1,2})?\n)+)")
SI_REGEX = re.compile(r"(EIS|DWE|DOE|AWE|AOE|ALU|GPU|ITR) *(?:(A) *([AB])?|(\d{1,2}))?")
ASSEMBLY_REGEX = re.compile(r"([A-Z]{2,5}) *([\d;$a-z]*(?:&.)?)")

frequency = 1  # Hz
language_definition_file = "AssemblX-deffile.axs"
debug = False

arg_str = ""
for i in range(2, len(sys.argv)):
	arg_str += sys.argv[i] + " "
arg_str = arg_str.strip()

for match in ARG_REGEX.finditer(arg_str):
	if match.group(1) is not None:
		frequency = int(match.group(1))
	elif match.group(2) is not None:
		language_definition_file = match.group(2)
	elif match.group(3) is not None:
		debug = True

with open(language_definition_file) as f:
	ld_raw = f.read()

ld = {}

for match in AXS_REGEX.finditer(ld_raw):
	ld[match.group(1)] = match.group(2).split("\n")

print(ld)

if len(ld.keys()) != 16:
	if debug:
		print(f"{len(ld.keys())}/16 keys present")
	sys.exit("0x1")

ad_mirror = False

we_index = -2
oe_index = -2
awe_index = -2

PLACEHOLDER_LOOKUP = {
	"$a": 1,
	"$b": 2,
	"$c": 3,
	"$d": 4,
	"$ram": 10,
	"$gram": 11,
	"$alua": 5,
	"$alub": 6,
	"$aluc": 7,
	"$aluoa": 8,
	"$aluob": 9,
	"$exi1": 12,
	"$exi2": 13,
	"$exi3": 14,
	"$exi4": 15,
	"$exo1": 16,
	"$exo2": 17,
	"$exo3": 18,
	"$exo4": 19
}

DWE_LOOKUP = {
	1: 0,
	2: 1,
	3: 2,
	4: 3,
	5: 4,
	6: 10,
	7: 5,
	8: 6,
	9: 7,
	10: -1,
	11: 11,
	12: 12,
	13: 13,
	14: 14,
	15: 15
}

DOE_LOOKUP = {
	1: 0,
	2: 1,
	3: 2,
	4: 3,
	5: 4,
	6: 10,
	7: -1,
	8: 8,
	9: 9,
	10: 16,
	11: 17,
	12: 18,
	13: 19,
}

mem_locs = [
	0,  # dep
	0,  # a
	0,  # b
	0,  # c
	0,  # d
	0,  # alu a
	0,  # alu b
	0,  # alu c
	0,  # alu oa
	0,  # alu ob
	{},  # ram
	[
		{},
		{}
	],
	0,
	0,
	0,
	0,
	0,
	0,
	0,
	0
]

line_counter = -1
ram_addr = 0
gram_addr = 0
alu_mode = 0
txt_gpu = True


def get_data(index: int):
	if index == 10:
		try:
			out = int(mem_locs[index][ram_addr])
		except KeyError:
			out = 0
	else:
		out = int(mem_locs[index])
	if debug:
		print(f"Fetching data from index {index}: {out}")
	return out


def set_data(index: int, value: int):
	if debug:
		print(f"Setting data at {index} to {value}")
	if index == 10:
		mem_locs[index][ram_addr] = value
	elif index == 11:
		mem_locs[index][int(txt_gpu)][gram_addr] = value
	else:
		mem_locs[index] = value


def parse_arg_input(arg: str):
	if debug:
		print(f"Parsing argument '{arg}'")
	if arg.startswith("b"):
		out = int(arg[1:], 2)
	elif arg.startswith("x"):
		out = int(arg[1:], 16)
	elif arg.startswith("o"):
		out = int(arg[1:], 8)
	elif arg.startswith("&"):
		out = ord(arg[1])
	else:
		out = int(arg)
	if debug:
		print(f"Parsing argument '{arg}' to integer {out}")
	return out


def gpu_render():
	if debug:
		print(f"Rendering")
	if txt_gpu:
		if debug:
			print(mem_locs[11][1])
		for value in mem_locs[11][1].values():
			print(chr(value), end='')
	else:
		sys.exit("0x7")


def gpu_clear():
	if debug:
		print("---")
	else:
		if os.name == "nt":
			os.system("cls")
		else:
			os.system("clear")


def run_si(si: str, args: str):
	global line_counter, ram_addr, gram_addr, we_index, oe_index, ad_mirror, awe_index, alu_mode, txt_gpu
	if args is not None:
		arg_s = [arg.strip() for arg in args.split(";")]
	else:
		arg_s = []

	if debug:
		print(f"Running subinstruction '{si}' ({args})")
	m = SI_REGEX.match(si)

	if m is None:
		if debug:
			print(f"Skipping non-instruction on line {line_counter}: '{si}'")
		return True

	if debug:
		print(m.groups())
		print(f"'{args}': {arg_s}")

	if m.group(1) == "EIS":
		if m.group(4) is None:
			mem_locs[0] = 0
			we_index = -2
			oe_index = -2
			awe_index = -2
			return False
		else:
			return bool(get_data(8))

	elif m.group(1) == "DWE":
		if m.group(2) is not None:
			if m.group(3) == "A":
				if not arg_s[0].startswith("$"):
					sys.exit("0x3")
				loc = PLACEHOLDER_LOOKUP[arg_s[0]]
			elif m.group(3) == "B":
				if not arg_s[1].startswith("$"):
					sys.exit("0x3")
				loc = PLACEHOLDER_LOOKUP[arg_s[1]]
			else:
				if not args.startswith("$"):
					sys.exit("0x3")
				loc = PLACEHOLDER_LOOKUP[args]
		else:
			loc = DWE_LOOKUP[int(m.group(4))]
		if loc not in DWE_LOOKUP.values():
			sys.exit("0x4")
		we_index = int(loc)

	elif m.group(1) == "DOE":
		if m.group(2) is not None:
			if m.group(3) == "A":
				if not arg_s[0].startswith("$"):
					sys.exit("0x3")
				loc = PLACEHOLDER_LOOKUP[arg_s[0]]
			elif m.group(3) == "B":
				if not arg_s[1].startswith("$"):
					sys.exit("0x3")
				loc = PLACEHOLDER_LOOKUP[arg_s[1]]
			else:
				if not args.startswith("$"):
					sys.exit("0x3")
				loc = PLACEHOLDER_LOOKUP[args]
		else:
			loc = DOE_LOOKUP[int(m.group(4))]
		if loc not in DOE_LOOKUP.values():
			sys.exit("0x4")
		oe_index = int(loc)

	elif m.group(1) == "AWE":
		awe_index = int(m.group(4))
		if not (0 < awe_index <= 4):
			if debug:
				print(f"AWE failed: {m.groups()}")
			sys.exit("0x1")

	elif m.group(1) == "AOE":
		try:
			ad_mirror = bool(int(m.group(4)))
		except ValueError:
			if debug:
				print(f"AOE failed: {m.groups()}")
			sys.exit("0x1")

	elif m.group(1) == "ALU":
		if m.group(2) is not None:
			alu_mode = int(parse_arg_input(args))
		else:
			alu_mode = int(m.group(4))

	elif m.group(1) == "GPU":
		if len(arg_s) != 3:
			sys.exit("0x6")
		txt_gpu = bool(int(parse_arg_input(arg_s[0])))
		if bool(int(parse_arg_input(arg_s[1]))):
			gpu_render()
		if bool(int(parse_arg_input(arg_s[2]))):
			gpu_clear()

	elif m.group(1) == "ITR":
		sys.exit("0x7")

	else:
		if debug:
			print(f"Unknown subcom: {m.group(1)}")
		sys.exit("0x1")

	# Perform ALU operations
	alua = mem_locs[5]
	alub = mem_locs[6]
	aluc = mem_locs[7]

	aluob = 0

	if alu_mode == 0:
		aluoa = int(alua + alub + min(0, max(aluc, 1)))
		if aluoa >= 2 ** 32:
			aluob = aluoa - 2 ** 32
		if 0 > aluoa > 1:
			sys.exit("0x5")
	else:
		sys.exit("0x5")

	mem_locs[8] = aluoa
	mem_locs[9] = aluob

	# Moving values around when possible
	if we_index >= 0 and oe_index >= 0:
		set_data(we_index, get_data(oe_index))
	if ad_mirror and we_index == -1 and oe_index >= 0:
		if awe_index == 1:
			ram_addr = int(mem_locs[oe_index])
		elif awe_index == 2:
			gram_addr = int(mem_locs[oe_index])
		elif awe_index == 3:
			line_counter = int(mem_locs[oe_index]) - 1
		elif awe_index == 4:
			pass
	else:
		if awe_index == 1:
			ram_addr = int(parse_arg_input(args))
		elif awe_index == 2:
			gram_addr = int(parse_arg_input(args))
		elif awe_index == 3:
			line_counter = int(parse_arg_input(args)) - 1
		elif awe_index == 4:
			if oe_index == -1 and we_index >= 0:
				set_data(we_index, parse_arg_input(args))


with open(os.path.abspath(sys.argv[1])) as f:
	lines = f.readlines()

running = True

while running:
	line_counter += 1
	if debug:
		print(f"\nRunning line {line_counter}: '{lines[line_counter][:-1]}'")
		print(f"Memory dump: {mem_locs}")
	if line_counter >= len(lines):
		sys.exit("0xE")
	match = ASSEMBLY_REGEX.match(lines[line_counter])
	if match is not None:
		if debug:
			print(f"Subinstructions: {ld[match.group(1)]}")
		for subi in ld[match.group(1)]:
			running = run_si(subi, match.group(2))
		if list(ld.keys()).index(match.group(1)) == len(ld.keys()) - 1:
			sys.exit("0xF")
