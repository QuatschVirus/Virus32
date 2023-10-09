import sys
import os
import re

VARDEF = re.compile(r"(?P<type>int|bool|char|string) (?P<name>[a-zA-z0-9_-]+)(?P<ass> = .+)?;")
VERASS = re.compile(r"(?P<name>[a-zA-z0-9_-]+)(?P<ass> = .+);")

TOKENS = re.compile(
	r"(?P<string>\".*\")|"
	r"(?P<bool>true|false)|"
	r"(?P<char>'.')|"
	r"(?P<number>-?\d+)|"
	r"(?P<bracket>[()\[\]{}])|"
	r"(?P<type>int|bool|char|string)|"
	r"(?P<array_def>array)|"
	r"(?P<keyword>ref|blk|ublk|ret|brk|con|if|loop)|"
	r"(?P<operator>[+\-*/%=<>!&|?](?:=|==|\||\|\||&)?)|"
	r"(?P<end>;)|"
	r"(?P<def>:)|"
	r"(?P<comma>,)|"
	r"(?P<reference>[a-z-A-Z0-9_-]+)"
)


class Token:
	def __init__(self, identifier: str, value: str, ref_line: str, ref_ind: int):
		self.key = identifier
		self.value = value
		self.ref_line = ref_line
		self.ref_ind = ref_ind

	def __str__(self):
		return f"Token: {self.key} ({self.value})"


class SyntaxBranch:
	def __init__(self, key: str, branches: list, ref_line: str, ref_ind: int, **args):
		self.key = key
		self.args = dict(args)
		self.branches = branches
		self.ref_line = ref_line
		self.ref_ind = ref_ind


var_ram_assign = {}
highest_free_address = 0

tokens: list[Token] = []
syntax_tree: list[SyntaxBranch] = []
action_tree = []

depths = {
	"()": 0,
	"{}": 0,
	"[]": 0,
	";": 0
}


def throw(kind: str, message: str, line: str, line_i: int):
	print(f"Compiler error: {kind} in line {line_i}: '{line}'")
	print(message)
	sys.exit("Compiler error")


def gen_tokens(lines: list[str]):
	for i in range(len(lines)):
		for match in TOKENS.finditer(lines[i]):
			for k, v in match.groupdict().items():
				if v is not None:
					tokens.append(Token(k, v, lines[i], i))


def gen_syntax_tree(tks: list[Token]):
	global depths
	out = []
	while len(tks) > 0:
		t = tks.pop(0)
		if t.key == "type":
			if tks[0].key == "reference":
				depths[";"] += 1
				t1 = tks.pop(0)
				out.append(SyntaxBranch("create_var", gen_syntax_tree(tks), t.ref_line, t.ref_ind, type=t.value, name=t1.value))
			else:
				throw("SyntaxError", "Type keyword needs to be followed by a name", t.ref_line, t.ref_ind)

		if t.key == "array_def":
			t1 = tks.pop(0)
			if t1.key == "number":
				if int(t1.value) < 2:
					throw("SizeError", "Cannot create array shorter than two entries", t.ref_line, t.ref_ind)
				out.append(SyntaxBranch("create_array", gen_syntax_tree(tks), t.ref_line, t.ref_ind, size=int(t1.value)))
			else:
				throw("SyntaxError", "Array keyword needs to be followed by size as a number", t.ref_line, t.ref_ind)

		if t.key == "keyword":
			depths[";"] += 1
			translate = {
				"ref": "reference",
				"blk": "block",
				"ublk": "unblock",
				"ret": "return",
				"brk": "break",
				"con": "continue",
				"if": "if",
				"loop": "loop"
			}
			if t.key in ("if", "loop"):
				if tks[0].value != "(":
					throw(
						"SyntaxError",
						"If and Loop keywords need to be followed by a condition encased in parenthesis",
						t.ref_line, t.ref_ind)
				depths["()"] += 1
			out.append(SyntaxBranch(translate[t.value], gen_syntax_tree(tks), t.ref_line, t.ref_ind))

		elif t.key == "end":
			depths[";"] -= 1
			return out
	return out


def gen_subtree(line: str, line_i: int):
	global highest_free_address
	out = []
	if (m := VARDEF.match(line)) is not None:
		out.append({
			"action": "create_var",
			"type": m.group("type"),
			"name": m.group("name"),
			"address": highest_free_address
		})
		var_ram_assign[m.group("name")] = highest_free_address
		highest_free_address += 1
		if m.group("ass") is not None:
			out.append({
				"action": "assign_var",
				"name": m.group("name"),
				"address": var_ram_assign[m.group("name")],
				"value": gen_subtree(m.group("val"), line_i)
			})
	elif (m := VERASS.match(line)) is not None:
		try:
			out.append({
				"action": "assign_var",
				"name": m.group("name"),
				"address": var_ram_assign[m.group("name")],
				"value": gen_subtree(m.group("val"), line_i)
			})
		except KeyError:
			throw("NameError", "Name not found to reference a memory address. Check for spelling", line, line_i)
	else:
		throw(
			"UnknownStatementError",
			"The statement does not match any language keywords. Check if it should be a comment preceded by //",
			line, line_i)
		return None
	return out


if __name__ == "__main__":
	print("VL compiler")
	debug = "-v" in sys.argv
	fp = sys.argv[1]
	if debug:
		print(f"Compiling file: '{fp}'")
	if not os.path.exists(fp) or not fp.endswith('.vl'):
		sys.exit("Invalid source file")

	with open(fp, 'r') as f:
		code = f.readlines()

	gen_tokens(code)
	if debug:
		for token in tokens:
			print(str(token))
