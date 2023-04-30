from websockets.sync.client import connect
import ipaddress
import json
import random
import re
import requests
import uuid
import secrets


def _cookie(cookie_fname):
	with open(cookie_fname, "r") as f:
		return f.read().strip()


def _headers(cookie_fname):
	with open("headers.json", "r") as f:
		headers = json.load(f)
		headers["cookie"] = _cookie(cookie_fname)
		headers["x-ms-client-request-id"] = str(uuid.uuid4())
		headers["x-forwarded-for"] = ipaddress.IPv6Address._string_from_ip_int(random.randint(0, ipaddress.IPv6Address._ALL_ONES))
		return headers


def _create_conversation(cookie_fname):
	response = requests.get("https://www.bing.com/turing/conversation/create", headers=_headers(cookie_fname))
	data = response.json()
	return data["conversationId"], data["clientId"], data["conversationSignature"]


def _socket_msg(obj):
	return json.dumps(obj) + "\x1e"


def _initial_handshake_msg():
	obj = {
		"protocol": "json",
		"version": 1
	}
	return _socket_msg(obj)


def _balanced():
	return ["glpromptv6p", "galileo"]


def _creative():
	return ["h3imaginative", "clgalileo", "gencontentv3"]


def _precise():
	return ["h3precise", "clgalileo"]


def _chathub_ws_msg(msg, cookie_fname, cdxtone=_creative()):
	conv_id, client_id, conv_sig = _create_conversation(cookie_fname)
	with open("websocket.json", "r") as f:
		obj = json.load(f)
		obj["arguments"][0]["traceId"] = secrets.token_hex(16)
		obj["arguments"][0]["conversationSignature"] = conv_sig
		obj["arguments"][0]["conversationId"] = conv_id
		obj["arguments"][0]["participant"]["id"] = client_id
		obj["arguments"][0]["message"]["text"] = msg
		for item in cdxtone:
			obj["arguments"][0]["optionsSets"].append(item)
		return _socket_msg(obj)


def _clean_msg(msg):
	msg = re.sub(r"\*\*", "", msg)
	msg = re.sub(r"\[\^([0-9])+\^\] *", "", msg).strip()
	return msg


def ask(client_msg, cookie_fname):
	with connect("wss://sydney.bing.com/sydney/ChatHub") as websocket:
		websocket.send(_initial_handshake_msg())
		websocket.recv()
		websocket.send(_chathub_ws_msg(client_msg, cookie_fname))
		while True:
			data = json.loads(websocket.recv().split("\x1e")[0])
			if data["type"] != 2:
				continue
			for msg in data["item"]["messages"]:
				if msg["author"] == "user":
					continue
				if "messageType" in msg:
					continue
				else:
					return _clean_msg(msg["text"])
				break


if __name__ == "__main__":
	root = "Comcast sued by former employee who accused Jeff Shell of harassment and discrimination A former employee of Comcast's NBCUniversal division has filed a lawsuit against the company and its former CEO Jeff Shell, alleging that she was subjected to sexual harassment and discrimination by Shell and that the company failed to protect her. The plaintiff, who is not named in the complaint, claims that Shell made unwanted sexual advances towards her, pressured her to have an affair with him, and retaliated against her when she rejected him. She also accuses Comcast of creating a hostile work environment and covering up Shell's misconduct."
	q = f'Write 5 sentences about Comcast that is not related to {root}.'
	print(ask(q, "cookie31.txt"))
