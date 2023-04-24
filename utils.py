import pathlib


def num_cookies():
	cookies = [item for item in pathlib.Path(__file__).parent.glob("cookie*.txt")]
	return len(cookies)

