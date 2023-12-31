import os
import sys
import re

if len(sys.argv) < 2:
    sys.exit("Error: No file given!")

p = sys.argv[1]

file_str = "v2.0 raw\n# Generated by AssemblX-Compiler.py by QuatschVirus\n"

if not os.path.exists(p):
    sys.exit("Not a valid path!")

if not p.endswith(".ax"):
    sys.exit("Not a .ax file")

with open(p) as f:
    content = f.read().replace("$$", "")

INTEGER_BASES = {
    "b": 2,
    "o": 8,
    "d": 10,
    "": 10,
    "x": 16
}

LOOKUP = ["NOP", "CD", "SD", "LD", "SMA", "SGMA", "CLD", "JMP", "DJMP", "JMPE", "IR", "GPU", "ALU", "$$", "$$", "HLT"]

COM_RE = re.compile(r"(NOP|CD|SD|LD|SMA|SGMA|CLD|JMP|DJMP|JMPE|IR|GPU|ALU|HLT) *(\d*[bxod]?[\da-f,]+)?")
ARG_RE = re.compile(r"(\d*)([bodx]?)([\da-f]+)")

for line in content.split("\n"):
    out = ""
    if (match := COM_RE.match(line)) is not None:
        print(line)
        com = format(LOOKUP.index(match.group(1)), "b")
        out += "0" * (4 - len(com)) + com
        arg_str = ""
        for arg in (args_split := match.group(2).split(",") if match.group(2) is not None else []):
            arg = arg.strip()
            arg_match = ARG_RE.match(arg)
            print(arg_match.groups())
            arg_bin = format(int(arg_match.group(3), INTEGER_BASES[arg_match.group(2)]), "b")
            arg_str += ("0" * (int(arg_match.group(1) if arg_match.group(1) != "" else (4 if len(args_split) > 1 else 32)) - len(arg_bin))) + arg_bin
        out += ("0" * (32 - len(arg_str))) + arg_str
        if len(out) > 36:
            sys.exit(f"Error: Expression \"{line}\" produced to long compile output ({len(out)}/36 bits)")
        file_str += (format(int(out, 2), "x") if int(out, 2) != 0 else "0" * 9) + "\n"
        
with open(p + "b", "w") as f:
    f.write(file_str)
