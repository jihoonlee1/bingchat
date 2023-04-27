import database


with database.connect() as con:
	cur = con.cursor()
	cur.execute("SELECT count(*), company_id FROM root_events GROUP BY company_id ORDER BY count(*) DESC")
	for count, company_id in cur.fetchall():
		if count != 5:
			print(f"root: {count}, {company_id}")

	cur.execute("SELECT count(*), company_id FROM root_event_children WHERE is_follow_up = 0 GROUP BY root_event_id ORDER BY count(*) DESC")
	for count, company_id in cur.fetchall():
		if count != 5:
			print(f"neg: {count}, {company_id}")

	cur.execute("SELECT count(*), company_id FROM root_event_children WHERE is_follow_up = 1 GROUP BY root_event_id ORDER BY count(*) DESC")
	for count, company_id in cur.fetchall():
		if count != 5:
			print(f"pos: {count}, {company_id}")
