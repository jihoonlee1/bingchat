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
	q0 = 'Write 3 news articles about company Apple on different topic. Separate each article with "Article: ".'
	root = '''Apple working on gaming and fitness apps for its AR headset
Apple is reportedly developing gaming and fitness apps for its upcoming augmented reality (AR) headset, which is expected to launch in 2022. According to Bloomberg, Apple has a team of engineers and designers working on creating apps that will showcase the capabilities of the AR device. The gaming app is said to be a multiplayer game that lets users interact with virtual objects in their environment. The fitness app is said to be similar to Apple Fitness+, but with AR elements that enhance the workout experience. Apple is also working on other apps for the headset, such as maps, messaging and video conferencing.'''
	q1 = f'Write 3 made up news articles that are direct follow-up to "{root}". Make sure each article is about company Apple. Separate each article with "Article: ".'
	diff_comp = '''Here are three made up news articles that are direct follow-up to "Apple working on gaming and fitness apps for its AR headset":

Article: Apple unveils Reality Pro headset at WWDC 2023
```
Apple has finally revealed its long-awaited augmented reality (AR) headset, dubbed Reality Pro, at its Worldwide Developers Conference (WWDC) 2023. The device, which is expected to launch in the summer, is a mixed reality headset that combines AR and VR features to create immersive experiences.

The Reality Pro headset features two micro OLED displays, one for each eye, that offer a 120-degree field of view and a high resolution. The device also has an adjustable interpupillary distance (IPD) range to fit different users. The headset is powered by the Apple M2 processor, which is designed for high-performance computing and graphics.

One of the main attractions of the Reality Pro headset is its app ecosystem, which includes gaming and fitness apps that showcase the capabilities of the device. The gaming app is a multiplayer game that lets users interact with virtual objects in their environment, such as throwing balls or shooting arrows. The fitness app is similar to Apple Fitness+, but with AR elements that enhance the workout experience, such as virtual trainers and scenery.

Apple also announced other apps for the headset, such as maps, messaging and video conferencing. The maps app allows users to explore different locations in AR, such as landmarks and museums. The messaging app lets users send and receive texts, emojis and stickers in AR. The video conferencing app enables users to have face-to-face meetings in VR, with realistic avatars and backgrounds.

The Reality Pro headset will cost $2,999 and will be available in three colors: black, white and silver. The device will also come with an external battery that can be attached magnetically to the user's pocket or belt. The battery will provide up to two hours of continuous use.

Apple CEO Tim Cook said that the Reality Pro headset is a "breakthrough product" that will "change the way we see and interact with the world". He also said that the device is "the most advanced and innovative product we have ever made".
```

Article: Apple partners with Netflix and Disney+ for Reality Pro headset
```
Apple has announced partnerships with Netflix and Disney+ to bring their streaming content to its upcoming Reality Pro headset. Users will be able to watch live sports, news and videos with immersive environments on the device.

Netflix and Disney+ will offer a selection of their original shows and movies in VR format, which will let users feel like they are inside the scenes. For example, users can watch Stranger Things in VR and explore the Upside Down, or watch The Mandalorian in VR and join the adventures of Baby Yoda.

Users will also be able to watch regular 2D content on a virtual screen that can be resized and positioned according to their preference. Users can also customize their viewing environment with different themes and ambiances, such as a cinema, a living room or a beach.

The Reality Pro headset will support spatial audio and Dolby Atmos for a realistic sound experience. Users will also be able to control their playback with hand gestures, voice commands or other Apple devices.

Netflix and Disney+ will charge an extra fee for their VR content, which will be added to their existing subscription plans. Users will need an internet connection to stream content on the Reality Pro headset.
```

Article: Apple faces backlash over Reality Pro headset design
```
Apple's Reality Pro headset has received mixed reactions from critics and consumers over its design. While some praised the device for its features and performance, others criticized it for its weight, size and appearance.

The Reality Pro headset weighs about 300 grams (0.66 pounds), which is heavier than most VR headsets on the market. Some users complained that the device was uncomfortable to wear for long periods of time and caused neck strain. Others said that the device was too bulky and looked like a "brick" on their face.

The Reality Pro headset also has a distinctive design that resembles a pair of sunglasses with thick frames. Some users said that the device looked stylish and futuristic, while others said that it looked ugly and awkward. Some users also expressed concerns about privacy and security issues when wearing the device in public.

Apple has defended its design choices for the Reality Pro headset, saying that they were necessary to achieve high-quality visuals and functionality. Apple also said that it was working on improving the comfort and ergonomics of the device for future versions.'''
	q2 = f'Replace Apple with a different company name in {diff_comp}.'
	print(ask(q2, "cookie29.txt"))
