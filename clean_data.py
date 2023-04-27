import database


with database.connect() as con:
	cur = con.cursor()
	cur.execute("SELECT count(*), company_id FROM root_events GROUP BY company_id")
	for count, company_id in cur.fetchall():
		if count != 5:
			cur.execute("DELETE FROM root_event_children WHERE company_id = ?", (company_id, ))
			cur.execute("DELETE FROM root_events WHERE company_id = ?", (company_id, ))
			cur.execute("DELETE FROM events WHERE company_id = ?", (company_id, ))
	con.commit()
