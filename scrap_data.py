import bing
import database
import queue
import threading
import re


WRITE_QUEUE = queue.Queue()
NUM_COOKIES = 12
NUM_COMPANIES_PER_COOKIE = 5
MAX_WORKERS = NUM_COMPANIES_PER_COOKIE * NUM_COOKIES


def _separate(response):
	pattern = re.compile(r"(Article *[0-9]*:)", re.IGNORECASE)
	temp = [item.strip() for item in pattern.split(response) if item != ""]
	answers = []
	for idx, item in enumerate(temp):
		if idx == 0 and not item.startswith("Article:"):
			continue
		else:
			if not item.startswith("Article:"):
				answers.append(item)
	return answers


def _initial_question(company_name):
	return f'''
	Write 5 made up news articles about {company_name} on different subject.
	Make sure each article is about {company_name}.
	Separate each article with "Article: ".
	'''


def _soft_pos_question(company_name, root_incident):
	return f'''
	Write 12 made up news articles that are direct follow-ups to {root_incident}.
	Make sure each article is about {company_name}.
	Separate each article with "Article: ".
	'''


def _soft_neg_question(company_name, root_incident):
	return f'''
	Write 2 made up news articles that are irrelevant to {root_incident}.
	Make sure each article is about {company_name}.
	Separate each article with "Article: ".
	'''


def _hard_neg_question0(company_name, root_incident):
	return f'''
	Write 2 made up news articles that are same to {root_incident}.
	Make sure each article is not about {company_name}, and make sure to use different company name for each article.
	Separate each article with "Article: ".
	'''


def _hard_neg_question1(company_name, root_incident):
	return f'''
	Write 2 made up news articles that are similar to {root_incident}.
	Make sure each article is not about {company_name}, and make sure to use different company name for each article.
	Separate each article with "Article: ".
	'''


def _hard_neg_question2(company_name, root_incident):
	return f'''
	Write 2 made up news articles follow-ups to {root_incident}. But replace {company_name} with a different company name for each article.
	Make sure each article is about {company_name}.
	Separate each article with "Article: ".
	'''


def _scrap(company_id, company_name, cookie):
	try:
		root_incidents = _separate(bing.ask(_initial_question(company_name), cookie))
	except:
		WRITE_QUEUE.put(None)
		return
	for root_incident in root_incidents:
		try:
			data = []
			data.append((company_id, company_name))
			data.append(root_incident)
			soft_pos = _separate(bing.ask(_soft_pos_question(company_name, root_incident), cookie))
			soft_neg = _separate(bing.ask(_soft_neg_question(company_name, root_incident), cookie))
			hard_neg0 = _separate(bing.ask(_hard_neg_question0(company_name, root_incident), cookie))
			hard_neg1 = _separate(bing.ask(_hard_neg_question1(company_name, root_incident), cookie))
			hard_neg2 = _separate(bing.ask(_hard_neg_question2(company_name, root_incident), cookie))

			for item in soft_pos:
				data.append((item, 1))
			for item in soft_neg:
				data.append((item, 0))
			for item in hard_neg0:
				data.append((item, 0))
			for item in hard_neg1:
				data.append((item, 0))
			for item in hard_neg2:
				data.append((item, 0))

			WRITE_QUEUE.put(data)
		except:
			continue
	WRITE_QUEUE.put(None)


def _write():
	with database.connect() as con:
		num_workers = MAX_WORKERS
		cur = con.cursor()

		while num_workers > 0:
			item = WRITE_QUEUE.get()
			if item is None:
				num_workers -= 1
				print(f"A worker finished its job. ({num_workers}/{MAX_WORKERS})")
			else:
				company_id, company_name = item[0]
				print(f"Writing {company_name}")
				root_incident = item[1]
				cur.execute("SELECT ifnull(max(id)+1, 0) FROM incidents")
				root_incident_id, = cur.fetchone()
				cur.execute("INSERT INTO incidents VALUES(?,?,?)", (root_incident_id, company_id, root_incident))
				cur.execute("INSERT INTO root_incidents VALUES(?,?)", (root_incident_id, company_id))

				for content, is_follow_up in item[2:]:
					cur.execute("SELECT ifnull(max(id)+1, 0) FROM incidents")
					child_incident_id, = cur.fetchone()
					cur.execute("INSERT INTO incidents VALUES(?,?,?)", (child_incident_id, company_id, content))
					cur.execute("INSERT INTO root_incident_children VALUES(?,?,?,?)", (root_incident_id, child_incident_id, company_id, is_follow_up))
				con.commit()


def main():
	with database.connect() as con:
		write_db_thread = threading.Thread(target=_write)
		write_db_thread.start()

		scrap_threads = []
		cur = con.cursor()
		cur.execute("SELECT id, name FROM companies WHERE id NOT IN (SELECT DISTINCT company_id FROM root_incidents)")
		all_companies = cur.fetchall()

		leftend = 0
		rightend = NUM_COMPANIES_PER_COOKIE

		for i in range(NUM_COOKIES):
			companies = all_companies[leftend:rightend]
			for company_id, company_name in companies:
				t = threading.Thread(target=_scrap, args=(company_id, company_name, f"cookie{i}.json"))
				t.start()
				threads.append(t)
			leftend = rightend
			rightend = rightend + NUM_COMPANIES_PER_COOKIE

		for t in threads:
			t.join()

		write_db_thread.join()


if __name__ == "__main__":
	main()
