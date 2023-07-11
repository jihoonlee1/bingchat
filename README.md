# Binghello


## Introduction
I reverse engineered Bing Chat to use it with Python script. ChatGPT API was too expensive and I needed lots of data, so this was my hacky alternative.

## Usage
1. First, you need to grab your cookie on Bing Chat. Whenever you initiate a conversation (by talking on Bing Chat), there is a network connection made called `create`. Grab the cookie from this endpoint by looking at the network inspector.
2. After you grab a cookie, create a new text file inside this directory with your cookie string.
3. Pass in your cookie filename.
```
import binghello


cookie_filename = "cookie.txt"
conversation_id, client_id, conversation_signature = binghello.session(cookie_filename)
response = binghello.ask(question, conversation_id, client_id, conversation_signature, session_start=1)
print(response)
```
4. That's it!

## Caveat
- Bing Chat only allows 200 requests per 24 hours.
- My implementation of this reverse engineering is not asyncio. If you want to make concurrent requests, you have to multithread it. That is what I did for few of my projects.