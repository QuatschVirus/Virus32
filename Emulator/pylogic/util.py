import os
import json

metadata_path = "/simulation-metadata"


def update_ram_dump(name: str, data: list[int]):
	with open(os.path.join(metadata_path, "ram_dump.json"), "r") as f:
		dump = json.load(f)
	dump[name] = data
	with open(os.path.join(metadata_path, "ram_dump.json"), "w") as f:
		json.dump(dump, f)


def fetch_ram_dump(name: str):
	with open(os.path.join(metadata_path, "ram_dump.json"), "r") as f:
		dump = json.load(f)
	try:
		return dump[name]
	except KeyError:
		return None
