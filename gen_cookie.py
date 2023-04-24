import json
import pathlib


def _read_textfile(fname="cookie_str.txt"):
	with open(fname, "r") as f:
		return f.read().strip()


def _cookie_filename():
	temp = [int(item.stem.replace("cookie", "")) for item in pathlib.Path(__file__).parent.glob("cookie*.json")]
	temp = sorted(temp)
	cookie_idx = temp[-1] + 1
	return f"cookie{cookie_idx}.json"


def _cookie_str_to_obj(cookie_str):
	cookie_obj = {}
	cookie_list = cookie_str.split("; ")
	for item in cookie_list:
		key, val = item.split("=", 1)
		cookie_obj[key] = val
	return cookie_obj


def _write(obj, fname=_cookie_filename()):
	with open(fname, "w") as f:
		f.write(json.dumps(obj, indent="\t"))


def main():
	cookie_str = _read_textfile()
	cookie_obj = _cookie_str_to_obj(cookie_str)
	_write(cookie_obj)


if __name__ == "__main__":
	main()
