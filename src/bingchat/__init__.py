from websockets.sync.client import connect
import ipaddress
import json
import random
import re
import requests
import uuid
import secrets
import os


def _fpath(fname):
	return os.path.join(os.path.dirname(__file__), fname)


def _cookie_to_str(cookie_fname):
	with open(cookie_fname) as f:
		data = json.load(f)
		cookie = []
		for item in data:
			name = item["name"].strip()
			value = item["value"].strip()
			line = name + "=" + value
			cookie.append(line)
		cookie = "; ".join(cookie)
		return cookie


def _cookie(cookie_fname):
	cookie = _cookie_to_str(cookie_fname)
	return cookie


def _headers(cookie_fname):
	with open(_fpath("headers.json"), "r") as f:
		headers = json.load(f)
		headers["cookie"] = _cookie(cookie_fname)
		headers["x-ms-client-request-id"] = str(uuid.uuid4())
		headers["x-forwarded-for"] = ipaddress.IPv6Address._string_from_ip_int(random.randint(0, ipaddress.IPv6Address._ALL_ONES))
		return headers


def session(cookie_fname):
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


def _chathub_ws_msg(msg, conv_id, client_id, conv_sig, session_start, cdxtone=_creative()):
	with open(_fpath("websocket.json"), "r") as f:
		obj = json.load(f)
		if session_start:
			obj["arguments"][0]["isStartOfSession"] = True
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


def ask(client_msg, session, session_start=False):
	conv_id, client_id, conv_sig = session
	with connect("wss://sydney.bing.com/sydney/ChatHub") as websocket:
		websocket.send(_initial_handshake_msg())
		websocket.recv()
		websocket.send(_chathub_ws_msg(client_msg, conv_id, client_id, conv_sig, session_start))
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

