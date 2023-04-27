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
	# question = "Write 5 made-up news articles about Berkshire Hathaway."
	root_incident = '''Berkshire Hathaway launches its own streaming service
Berkshire Hathaway, the diversified holding company owned by Warren Buffett, has announced the launch of its own streaming service, called BH TV. The service will offer exclusive content from Berkshire Hathaway's subsidiaries and partners, such as Geico, Dairy Queen, Coca-Cola, Apple, and Amazon. The service will also feature original shows and documentaries about Buffett's life and investment philosophy, as well as interviews with celebrities and business leaders. BH TV will be available for $9.99 per month or $99 per year.'''
	question = f'Write 5 made up news articles that are direct follow-up to {root_incident}. Make sure each article is about Berkshire Hathaway.'
	answer = ask(question, "cookie29.txt")
	print(answer)
