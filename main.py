import bing


def main():
	cookie_fname = ""  # Your cookie
	question = "Hello, bing!"
	response = bing.ask(question, cookie_fname)
	print(response)


if __name__ == "__main__":
	main()
	
