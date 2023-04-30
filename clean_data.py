import database
import re


def main():
	with database.connect() as con:
		cur = con.cursor()
		cur.execute("SELECT id, content FROM events")
		for event_id, content in cur.fetchall():
			content = content.strip()
			cur.execute("UPDATE events SET content = ? WHERE id = ?", (content, event_id, ))
		con.commit()


if __name__	== "__main__":
	main()
