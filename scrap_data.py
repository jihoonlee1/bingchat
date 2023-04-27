import bing
import database
import queue
import threading
import utils
import re


QUEUE = queue.Queue()
NUM_COOKIES = utils.num_cookies()
NUM_COMPANIES_PER_COOKIE = 10
MAX_WORKERS = NUM_COMPANIES_PER_COOKIE * NUM_COOKIES


def _answers(text):
	scenarios = [item for item in text.split("\n") if item != ""]
	if len(scenarios) == 6:
		scenarios = scenarios[1:]
	return scenarios


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
				root_scenario = item[1]
				child_scenarios = item[2:]
				cur.execute("SELECT ifnull(max(id)+1, 0) FROM scenarios")
				root_id, = cur.fetchone()
				cur.execute("INSERT INTO scenarios VALUES(?,?,?)", (root_id, company_id, root_scenario))
				cur.execute("INSERT INTO root_scenarios VALUES(?,?)", (root_id, company_id))
				for child_content, is_follow_up in child_scenarios:
					cur.execute("SELECT ifnull(max(id)+1, 0) FROM scenarios")
					child_id, = cur.fetchone()
					cur.execute("INSERT INTO scenarios VALUES(?,?,?)", (child_id, company_id, child_content))
					cur.execute("INSERT INTO root_scenario_children VALUES(?,?,?,?)", (root_id, child_id, company_id, is_follow_up))
				print(f"Inserting {company_name}.")
				con.commit()


def _scrap(company_id, company_name, cookie_fname):
	try:
		root_scenarios = _answers(bing.ask(f"Write 5 made up stories about {company_name} on different subject.", cookie_fname))
		print(f"root: {len(root_scenarios)}")
		for root_scenario in root_scenarios:
			data = []
			data.append((company_id, company_name))
			data.append(root_scenario)
			follow_up_scenarios = _answers(bing.ask(f'Write 5 possible scenarios that could happen after "{root_scenario}". Make sure each scenario is about {company_name}.', cookie_fname))
			irrelevant_scenarios = _answers(bing.ask(f'Write 5 scenarios that are irrelevant to "{root_scenario}". Make sure each scenario is about {company_name}.' cookie_fname))
			print(f"soft_pos: {len(follow_up_scenarios)}")
			print(f"soft_neg: {len(irrelevant_scenarios)}")
			for follow_up_scenario in follow_up_scenarios:
				data.append((follow_up_scenario, 1))
			for irrelevant_scenario in irrelevant_scenarios:
				data.append((irrelevant_scenario, 0))
			QUEUE.append(data)
	except:
		print(f"{cookie_fname} failed.")
		QUEUE.append(None)
		return
	QUEUE.append(None)


def main():
	with database.connect() as con:
		write_thread = threading.Thread(target=_write_to_db)
		write_thread.start()

		cur = con.cursor()
		cur.execute("SELECT id, name FROM companies WHERE id NOT IN (SELECT DISTINCT company_id FROM root_scenarios)")
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

		for t in threads:
			t.join()

		write_thread.join()


if __name__ == "__main__":
	main()
