import bing
import database
import queue
import threading
import utils
import re
import random


QUEUE = queue.Queue()
NUM_COOKIES = utils.num_cookies()
NUM_COMPANIES_PER_COOKIE = 2
MAX_WORKERS = NUM_COMPANIES_PER_COOKIE * NUM_COOKIES


def _answers(text):
	temp = [item.strip() for item in re.split(r"(Article:)", text, flags=re.IGNORECASE)]
	start_pos = 0
	for idx, item in enumerate(temp):
		if item.lower().startswith("article:"):
			start_pos = idx
			break
	events = []
	temp = temp[start_pos:]
	temp = [item for item in temp if item != "" and not item.lower().startswith("article:")]
	for item in temp:
		item = item.replace("```", "")
		item = re.sub(r"\n+", " ", item)
		events.append(item)
	return events


def _write_to_db():
	with database.connect() as con:
		cur = con.cursor()
		num_workers = MAX_WORKERS
		while True:
			if num_workers == 0:
				break
			item = QUEUE.get()
			if item is None:
				num_workers -= 1
				print(f"{num_workers}/{MAX_WORKERS} finished its job.")
			else:
				company_id, company_name = item[0]
				root0 = item[1]
				root_event0 = root0[0]
				rest_events0 = root0[1:]

				cur.execute("SELECT ifnull(max(id)+1, 0) FROM events")
				root_id0, = cur.fetchone()
				cur.execute("INSERT INTO events VALUES(?,?,?)", (root_id0, company_id, root_event0))
				cur.execute("INSERT INTO root_events VALUES(?,?)", (root_id0, company_id))
				for child_content, is_follow_up in rest_events0:
					cur.execute("SELECT ifnull(max(id)+1, 0) FROM events")
					child_id0, = cur.fetchone()
					cur.execute("INSERT INTO events VALUES(?,?,?)", (child_id0, company_id, child_content))
					cur.execute("INSERT INTO root_event_children VALUES(?,?,?,?)", (root_id0, child_id0, company_id, is_follow_up))

				print(f"Inserting {company_name}")
				con.commit()


def root_question(company_name):
	return f'Write 5 news stories about company "{company_name}" on different subject. Separate each story with "Article: ".'


def pos_question(company_name, root_event):
	return f'Write 5 possible news stories about company "{company_name}" that are considered direct follow-ups to "{root_event}". Make sure company "{company_name}" in each of the article. Separate each story with "Article: ".'


def neg_question(company_name, root_event):
	return f'Write 5 news stories about company "{company_name}" that are completely irrelevant to "{root_event}". Make sure company "{company_name}" is in each of the article. Separate each story with "Article: ".'


def _scrap(company_id, company_name, random_company_names, len_random_company_names, cookie_fname):
	try:
		root_events = _answers(bing.ask(root_question(company_name), cookie_fname))
		print(f"{company_name} root: {len(root_events)}")
		for root_event0 in root_events:
			data = []
			data.append((company_id, company_name))
			pos_events0= _answers(bing.ask(pos_question(company_name, root_event0), cookie_fname))
			neg_events0 = _answers(bing.ask(neg_question(company_name, root_event0), cookie_fname))

			print(len(pos_events0))
			print(len(neg_events0))

			root_container0 = []
			root_container0.append(root_event0)

			for event in pos_events0:
				root_container0.append([event, 1])
			for event in neg_events0:
				root_container0.append([event, 0])

			data.append(root_container0)
			QUEUE.put(data)
	except Exception as e:
		print(e)
		QUEUE.put(None)
		return
	QUEUE.put(None)


def main():
	with database.connect() as con:
		write_thread = threading.Thread(target=_write_to_db)
		write_thread.start()

		cur = con.cursor()
		cur.execute("SELECT id, name FROM companies WHERE id NOT IN (SELECT DISTINCT company_id FROM root_events)")
		companies = cur.fetchall()
		scrap_threads = []
		leftend = 0
		rightend = NUM_COMPANIES_PER_COOKIE

		for i in range(NUM_COOKIES):
			target_companies = companies[leftend:rightend]
			for company_id, company_name in target_companies:
				cur.execute("SELECT name FROM companies WHERE id != ?", (company_id, ))
				random_company_names = cur.fetchall()
				len_random_company_name = len(random_company_names)
				t = threading.Thread(target=_scrap, args=(company_id, company_name, random_company_names, len_random_company_name, f"cookie{i}.txt"))
				t.start()
				scrap_threads.append(t)
			leftend = rightend
			rightend = rightend + NUM_COMPANIES_PER_COOKIE

		for t in scrap_threads:
			t.join()

		write_thread.join()


if __name__ == "__main__":
	main()
