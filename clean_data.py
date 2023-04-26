import database


with database.connect() as con:
	cur = con.cursor()
	cur.execute("SELECT id FROM incidents WHERE length(content) < 200")
	ids = cur.fetchall()
	for inc_id, in ids:
		cur.execute("DELETE FROM root_incident_children WHERE child_incident_id = ?", (inc_id, ))
		cur.execute("DELETE FROM incidents WHERE id = ?", (inc_id, ))
	con.commit()
