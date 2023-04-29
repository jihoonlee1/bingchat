import bing
import database
import queue
import threading
import utils
import re


QUEUE = queue.Queue()
NUM_COOKIES = utils.num_cookies()
NUM_COMPANIES_PER_COOKIE = 5
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
				root1 = item[2]
				root_event0 = root0[0]
				root_event1 = root1[0]
				rest_events0 = root0[1:]
				rest_events1 = root1[1:]
				cur.execute("SELECT ifnull(max(id)+1, 0) FROM events")
				root_id0, = cur.fetchone()
				cur.execute("INSERT INTO events VALUES(?,?,?)", (root_id0, company_id, root_event0))
				cur.execute("INSERT INTO root_events VALUES(?,?)", (root_id0, company_id))
				for child_content, is_follow_up in rest_events0:
					cur.execute("SELECT ifnull(max(id)+1, 0) FROM events")
					child_id0, = cur.fetchone()
					cur.execute("INSERT INTO events VALUES(?,?,?)", (child_id0, company_id, child_content))
					cur.execute("INSERT INTO root_event_children VALUES(?,?,?,?)", (root_id0, child_id0, company_id, is_follow_up))

				cur.execute("SELECT ifnull(max(id)+1, 0) FROM events")
				root_id1, = cur.fetchone()
				cur.execute("INSERT INTO events VALUES(?,?,?)", (root_id1, company_id, root_event1))
				cur.execute("INSERT INTO root_events VALUES(?,?)", (root_id1, company_id))
				for child_content, is_follow_up in rest_events1:
					cur.execute("SELECT ifnull(max(id)+1, 0) FROM events")
					child_id1, = cur.fetchone()
					cur.execute("INSERT INTO events VALUES(?,?,?)", (child_id1, company_id, child_content))
					cur.execute("INSERT INTO root_event_children VALUES(?,?,?,?)", (root_id1, child_id1, company_id, is_follow_up))
				print(f"Inserting {company_name}")
				con.commit()


def _scrap(company_id, company_name, cookie_fname):
	try:
		root_events = _answers(bing.ask(f'Write 3 news articles about company {company_name} on different topic. Separate each article with "Article: ".', cookie_fname))
		print(f"{company_name} root: {len(root_events)}")
		for root_event0 in root_events:
			data = []
			data.append((company_id, company_name))
			temp0 = bing.ask(f'Write 3 made up news articles that are direct follow-up to "{root_event0}". Make sure each article is about company {company_name}. Separate each article with "Article: ".', cookie_fname)
			temp1 = bing.ask(f'Replace {company_name} with a different company name in {temp0}', cookie_fname)
			pos_events0 = _answers(temp0)
			neg_events0 = _answers(bing.ask(f'Write 3 made-up news articles that are irrelevant to "{root_event0}". Make sure each article is about company {company_name}. Separate each article with "Article: ".', cookie_fname))
			neg_events1 = _answers(temp1)
			root_event1 = neg_events0[0]
			pos_events1 = _answers(bing.ask(f'Write 3 made-up news articles that are direct follow-up to "{root_event1}". Make sure each article is about company {company_name}. Separate each article with "Article: ".', cookie_fname))
			print(f"{company_name} pos0: {len(pos_events0)}")
			print(f"{company_name} pos1: {len(pos_events1)}")
			print(f"{company_name} neg0: {len(neg_events0)}")
			print(f"{company_name} neg1: {len(neg_events1)}")

			root0_container = []
			root0_container.append(root_event0)
			for pos_event in pos_events0:
				root0_container.append((pos_event, 1))
			for neg_event in neg_events0:
				root0_container.append((neg_event, 0))
			for neg_event in neg_events1:
				root0_container.append((neg_event, 0))
			data.append(root0_container)

			root1_container = []
			root1_container.append(root_event1)
			for pos_event in pos_events1:
				root1_container.append((pos_event, 1))
			data.append(root1_container)
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
				t = threading.Thread(target=_scrap, args=(company_id, company_name, f"cookie{i}.txt"))
				t.start()
				scrap_threads.append(t)
			leftend = rightend
			rightend = rightend + NUM_COMPANIES_PER_COOKIE

		for t in scrap_threads:
			t.join()

		write_thread.join()


if __name__ == "__main__":
	main()
