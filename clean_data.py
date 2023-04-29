import database
import re


def remove_garbage(con, cur):
	cur.execute("SELECT id, content FROM events")
	for event_id, content in cur.fetchall():
		if len(content) < 250 or content.lower().startswith("here are") or content.lower().startswith("i can") or content.lower().startswith("i'm sorry"):
			cur.execute("SELECT 1 FROM root_events WHERE id = ?", (event_id, ))
			if cur.fetchone() is not None:
				cur.execute("SELECT child_event_id FROM root_event_children WHERE root_event_id = ?", (event_id, ))
				for temp_id, in cur.fetchall():
					cur.execute("DELETE FROM root_event_children WHERE child_event_id = ?", (temp_id, ))
					cur.execute("DELETE FROM events WHERE id = ?", (temp_id, ))
				cur.execute("DELETE FROM root_events WHERE id = ?", (event_id, ))
				cur.execute("DELETE FROM events WHERE id = ?", (event_id, ))
			cur.execute("SELECT 1 FROM root_event_children WHERE child_event_id = ?", (event_id, ))
			if cur.fetchone() is not None:
				cur.execute("DELETE FROM root_event_children WHERE child_event_id = ?", (event_id, ))
				cur.execute("DELETE FROM events WHERE id = ?", (event_id, ))
			con.commit()


def clean_text(con, cur):
	cur.execute("SELECT id, content FROM events")
	for event_id, content in cur.fetchall():
		content = content.strip()
		content = re.sub(r".+company name: #", "", content)
		content = re.sub(r".+like this: #", "", content)
		content = re.sub(r"^#", "", content)
		content = content.strip()
		cur.execute("UPDATE events SET content = ? WHERE id = ?", (content, event_id))
	con.commit()


if __name__ == "__main__":
	with database.connect() as con:
		cur = con.cursor()
		cur.execute("SELECT count(*) FROM events")
		before, = cur.fetchone()
		print(f"Before: {before}")
		remove_garbage(con, cur)
		clean_text(con, cur)
		cur.execute("SELECT count(*) FROM events")
		after, = cur.fetchone()
		print(f"After: {after}")
