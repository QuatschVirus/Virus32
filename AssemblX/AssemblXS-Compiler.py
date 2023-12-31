import os
import sys
import re

LOOKUP = ("EIS", "DWE", "DOE", "AWE", "AOE", "ALU", "GPU", "ITR")
SUBCOM_RE = re.compile(r"(EIS|DWE|DOE|AWE|AOE|ALU|GPU|ITR) *(?:(A) *([AB])?|(\d))?")

OUT_FILE = "AssemblX-definition.hex"


if len(sys.argv) < 2:
    sys.exit("Error: No file given!")

p = sys.argv[1]

file_str = "v2.0 raw\n# Generated by AssemblXS-Compiler.py by QuatschVirus\n"

if not os.path.exists(p):
    sys.exit("Not a valid path!")

if not p.endswith(".axs"):
    sys.exit("Not a .axs file")

with open(p) as f:
    content = f.read()

for command in re.split(r"//.*", content, maxsplit=16):
    command = command.strip()
    out = ""
    for line in command.split("\n"):
        if (match := SUBCOM_RE.match(line)) is not None:
            subcom_b = ""
            subcom = format(LOOKUP.index(match.group(1)), "b")
            subcom_b += "0" * (3 - len(subcom)) + subcom
            subcom_b += "1" if match.group(3) == "A" else "0"
            subcom_b += "1" if match.group(2) is not None else "0"
            if match.group(4) is not None:
                subcom_arg = format(int(match.group(4)), "b")
                subcom_b += "0" * (4 - len(subcom_arg)) + subcom_arg
            else:
                subcom_b += "0000"
            out += subcom_b
    if len(out) >= 9:
        file_str += (format(int(out + "0" * (63 - len(out)), 2), "x") if int(out, 2) != 0 else "0" * 16) + "\n"
    elif len(out) > 63:
        sys.exit(f"Error: Expression \"{command}\" produced to long compile output ({len(out)}/63 bits)")

with open(OUT_FILE, "w") as f:
    f.write(file_str)
