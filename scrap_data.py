import bing
import database
import queue
import threading
import utils
import re


QUEUE = queue.Queue()
NUM_COOKIES = utils.num_cookies()
NUM_COMPANIES_PER_COOKIE = 3
MAX_WORKERS = NUM_COMPANIES_PER_COOKIE * NUM_COOKIES


def _answers(text):
	events = [
		item for item in text.split("\n")
		if item != "" and
		not item.lower().startswith("here are") and
		not item.startswith("```") and
		not item.lower().startswith("i hope")
		and not item.lower().startswith("hello")]
	len_events = len(events)
	if len_events == 6:
		events = events[1:]
	elif len_events == 7:
		events = events[1:6]
	elif len_events == 10:
		temp = []
		for i in range(0, 10, 2):
			title, body = events[i], events[i+1]
			content = title + "\n" + body
			temp.append(content)
		return temp
	elif len_events == 11:
		temp = []
		events = events[1:]
		for i in range(0, 10, 2):
			title, body = events[i], events[i+1]
			content = title + "\n" + body
			temp.append(content)
		return temp
	elif len_events == 12:
		events = events[1:11]
		temp = []
		for i in range(0, 10, 2):
			title, body = events[i], events[i+1]
			content = title + "\n" + body
			temp.append(content)
		return temp
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
				root_event = item[1]
				child_events = item[2:]
				cur.execute("SELECT ifnull(max(id)+1, 0) FROM events")
				root_id, = cur.fetchone()
				cur.execute("INSERT INTO events VALUES(?,?,?)", (root_id, company_id, root_event))
				cur.execute("INSERT INTO root_events VALUES(?,?)", (root_id, company_id))
				for child_content, is_follow_up in child_events:
					cur.execute("SELECT ifnull(max(id)+1, 0) FROM events")
					child_id, = cur.fetchone()
					cur.execute("INSERT INTO events VALUES(?,?,?)", (child_id, company_id, child_content))
					cur.execute("INSERT INTO root_event_children VALUES(?,?,?,?)", (root_id, child_id, company_id, is_follow_up))
				print(f"Inserting {company_name}")
				con.commit()


def _scrap(company_id, company_name, cookie_fname):
	try:
		root_events = _answers(bing.ask(f"Write 5 made-up news stories about company {company_name} on different topics. Make sure each story is at least 30 words. ", cookie_fname))
		print(f"root: {len(root_events)} {company_name}")
		for root_event in root_events:
			data = []
			data.append((company_id, company_name))
			data.append(root_event)
			pos_events = _answers(bing.ask(f'Write 5 made-up news stories that are direct follow-up to "{root_event}". Make sure each story is about company {company_name}. Make sure each story is at least 30 words.', cookie_fname))
			neg_events = _answers(bing.ask(f'Write 5 made-up news stories that are irrelevant to "{root_event}". Make sure each story is about company {company_name}. Make sure each story is at least 30 words.', cookie_fname))

			print(f"soft_pos: {len(pos_events)} {company_name}")
			print(f"soft_neg: {len(neg_events)} {company_name}")
			for pos_event in pos_events:
				data.append((pos_event, 1))
			for neg_event in neg_events:
				data.append((neg_event, 0))
			QUEUE.put(data)
	except:
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
