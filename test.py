from websockets.sync.client import connect
import json


DELIMITER = "\x1e"


def _append_identifier(msg):
	return json.dumps(msg) + DELIMITER


def _handshake():
	obj = {
		"protocol": "json",
		"version": 1
	}
	return _append_identifier(obj)



{
	"arguments": [
		{
			"source":"cib",
			"optionsSets": [
				"nlu_direct_response_filter",
				"deepleo",
				"disable_emoji_spoken_text",
				"responsible_ai_policy_235",
				"enablemm",
				"h3imaginative",
				"clgalileo",
				"gencontentv3",
				"dlformfix",
				"responseos",
				"jb090",
				"jbfv202",
				"sportsansgnd",
				"dv3sugg"
			],
			"allowedMessageTypes": [
				"Chat",
				"InternalSearchQuery",
				"InternalSearchResult",
				"Disengaged",
				"InternalLoaderMessage",
				"RenderCardRequest",
				"AdsQuery",
				"SemanticSerp",
				"GenerateContentQuery",
				"SearchQuery"
			],
			"sliceIds": [
				"winmuid1tf",
				"contp2tf",
				"delayglobjscf",
				"0417bicunivs0",
				"audrngon",
				"sbsvgoptcf",
				"nopreloadsstf",
				"winstmsg2tf",
				"creatgoglc",
				"creatorv2t",
				"407dlformfix",
				"414suggs0",
				"scctl",
				"418glpv6p",
				"417rcallows0",
				"321slocs0",
				"0329resp",
				"418rchlths0",
				"asfixescf",
				"udscahrfoncf",
				"414jbfv202",
				"0416visuals0",
				"406sportgnd"
			],
			"verbosity": "verbose",
			"traceId": "64419bc7cf8d4181a3102b35137b3865",
			"isStartOfSession": True,
			"message": {
				"locale": "en-CA",
				"market": "en-CA",
				"region": "CA",
				"location": "lat:47.639557;long:-122.128159;re=1000m;",
				"locationHints": [
					{
						"country": "Canada",
						"state": "Ontario",
						"city": "North York",
						"zipcode": "m1l 4r9",
						"timezoneoffset": -5,
						"countryConfidence": 8,
						"cityConfidence": 8,
						"Center": {
							"Latitude": 43.7256,
							"Longitude": -79.3033
						},
						"RegionType": 2,
						"SourceType": 1
					}
				],
				"timestamp":"2023-04-20T16:08:40-04:00",
				"author":"user",
				"inputMethod":"Keyboard",
				"text":"can you tell me how your day has been?",
				"messageType":"Chat"
			},
			"conversationSignature":"ff3ky9UF/rVLcFBQ3oJczMbCJjFua6mdnLx2QJoF4lU=",
			"participant": {
				"id":"914799361211597"
			},
			"conversationId":"51D|BingProd|710CB728F86652A31C729A24B68697531B17C06264D47F0E842951C5C72996CA"
		}
	],
	"invocationId":"0",
	"target":"chat",
	"type":4
}
with connect("wss://sydney.bing.com/sydney/ChatHub") as websocket:
	websocket.send(append_identifier({"protocol": "json", "version": 1}))
	print(websocket.recv())
	websocket.send(append_identifier(test))
	print(websocket.recv())
