from websockets.sync.client import connect
import ipaddress
import json
import random
import re
import requests
import uuid
import secrets


def _cookie():
	with open("cookie.json", "r") as f:
		temp = json.load(f)
		cookie = []
		for key, val in temp.items():
			line = f"{key}={val}"
			cookie.append(line)
		cookie = "; ".join(cookie)
		return cookie


def _headers():
	with open("headers.json", "r") as f:
		headers = json.load(f)
		headers["cookie"] = _cookie()
		headers["x-ms-client-request-id"] = str(uuid.uuid4())
		headers["x-forwarded-for"] = ipaddress.IPv6Address._string_from_ip_int(random.randint(0, ipaddress.IPv6Address._ALL_ONES))
		return headers


def _create_conversation():
	response = requests.get("https://www.bing.com/turing/conversation/create", headers=_headers())
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


def _chathub_ws_msg(msg, cdxtone=_creative()):
	conv_id, client_id, conv_sig = _create_conversation()
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


def chat(client_msg):
	with connect("wss://sydney.bing.com/sydney/ChatHub") as websocket:
		websocket.send(_initial_handshake_msg())
		websocket.recv()
		websocket.send(_chathub_ws_msg(client_msg))
		while True:
			data = json.loads(websocket.recv().split("\x1e")[0])
			if data["type"] == 2:
				for msg in data["item"]["messages"]:
					if msg["author"] == "user":
						continue
					if "messageType" in msg:
						continue
					else:
						return _clean_msg(msg["text"])
				break


def main():
	msg = "Tell me about the 22nd president."
	response = chat(msg)
	print(response)


if __name__ == "__main__":
	main()


# def _create_chathub(rand_uuid4, rand_ipv6, conversation_id, client_id, conversation_signature):
# 	temp = random.randint(0, num_okay - 1)
# 	test["arguments"][0]["message"]["text"] = '''Write 3 made up news articles that are follow-up to "Apple launches its first car, the iCar, with self-driving and voice control features. The iCar is expected to compete with Tesla and other electric vehicle makers in the market. Apple claims that the iCar has a range of 500 miles on a single charge and can accelerate from 0 to 60 mph in 3 seconds. The iCar will be available in 2024 for $99,999.".'''
# 	test["arguments"][0]["participant"]["id"] = client_id
# 	test["arguments"][0]["conversationId"] = conversation_id
# 	test["arguments"][0]["conversationSignature"] = conversation_signature
# 	test["arguments"][0]["traceId"] = secrets.token_hex(16)
# 	with connect("wss://sydney.bing.com/sydney/ChatHub") as websocket:
# 		websocket.send(_initial_handshake())
# 		websocket.recv()
# 		websocket.send(_socket_msg(test))
# 		while True:
# 			data = json.loads(websocket.recv().split("\x1e")[0])
# 			if data["type"] == 2:
# 				for msg in data["item"]["messages"]:
# 					if msg["author"] == "user":
# 						continue
# 					if "messageType" in msg:
# 						continue
# 					else:
# 						print(msg["text"])
# 						break
# 				break



# def main():
# 	rand_uuid4, rand_ipv6, conversation_id, client_id, conversation_signature = _create_conversation()
# 	_create_chathub(rand_uuid4, rand_ipv6, conversation_id, client_id, conversation_signature)



# if __name__ == "__main__":
# 	main()


# d139b415-59d4-4c2f-aa3e-b9bd433a753d
