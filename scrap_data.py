import bing
import database
import queue
import time
import random
import threading


RESULT_QUEUE = queue.Queue()
SCRAP_QUEUE = queue.Queue()
MAX_WORKERS = 10


def _separate(response):
	pattern = re.compile(r"Article *[0-9]*:", re.IGNORECASE)
	answers = [item.strip() for item in pattern.split(response) if item != ""]
	return answers


def _companies(cur):
	companies = []
	cur.execute("SELECT id, name FROM companies LIMIT 20")
	for company_id, company_name in cur.fetchall():
		companies.append((company_id, company_name))
	return companies


def _initial_question(company_name):
	return f'''
	Write 5 made up news articles about {company_name} on different subject.
	Make sure each article is about {company_name}.
	Make sure each article is more than 50 words.
	Separate each article with "Article: ".
	'''


def _soft_pos_question(company_name, root_incident):
	return f'''
	Write 12 made up news articles that are direct follow-ups to {root_incident}.
	Make sure each article is about {company_name}.
	Make sure each article is more than 50 words.
	Separate each article with "Article: ".
	'''


def _soft_neg_question(company_name, root_incident):
	return f'''
	Write 3 made up news articles that are irrelevant to {root_incident}.
	Make sure each article is about {company_name}.
	Make sure each article is more than 50 words.
	Separate each article with "Article: ".
	'''


def hard_neg_question0(company_name, root_incident):
	return f'''
	Write 3 made up news articles that are same to {root_incident}.
	Make sure each article is not about {company_name}, and make sure to use different company name.
	Make sure each article is more than 50 words.
	Separate each article with "Article: ".
	'''


def hard_neg_question1(company_name, root_incident):
	return f'''
	Write 3 made up news articles that are similar to {root_incident}.
	Make sure each article is not about {company_name}, and make sure to use different company name.
	Make sure each article is more than 50 words.
	Separate each article with "Article: ".
	'''


def hard_neg_question2(company_name, root_incident):
	return f'''
	Write 3 made up news articles that are similar, but not direct follow-ups to {root_incident}.
	Make sure each article is about {company_name}.
	Make sure each article is more than 50 words.
	Separate reach article with "Article: ".
	'''


def _scrap():
	company_id, company_name = SCRAP_QUEUE.get()
	root_incidents = _separate(bing.ask(_initial_question(company_name)))
	print(len(root_incidents), company_name)

	for root_incident in root_incidents:
		soft_pos = _separate(bing.ask(_soft_pos_question(company_name, root_incident)))
		soft_neg = _separate(bing.ask(_soft_neg_question(company_name, root_incident)))
		hard_neg0 = _separate(bing.ask(_hard_neg_question0(company_name, root_incident)))
		hard_neg1 = _separate(bing.ask(_hard_neg_question1(company_name, root_incident)))
		hard_neg2 = _separate(bing.ask(_hard_neg_question2(company_name, root_incident)))
		print(f"Soft pos: {len(soft_pos)}")
		print(f"Soft neg: {len(soft_neg)}")
		print(f"Hard neg0: {len(hard_neg0)}")
		print(f"Hard neg1: {len(hard_neg1)}")
		print(f"Hard neg2: {len(hard_neg2)}")


def main():
	with database.connect() as con:
		cur = con.cursor()
		companies = _companies(cur)
		threads = []

		while len(companies) > 0:
			if SCRAP_QUEUE.qsize() < MAX_WORKERS:
				company_id, company_name = companies.pop(0)
				SCRAP_QUEUE.put((company_id, company_name))
				thread = threading.Thread(target=_scrap)
				thread.start()
				threads.append(thread)

		for t in threads:
			t.join()


if __name__ == "__main__":
	main()
