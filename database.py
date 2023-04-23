import json
import contextlib
import sqlite3


statements = [
"""
CREATE TABLE IF NOT EXISTS companies(
	id           INTEGER NOT NULL PRIMARY KEY,
	name         TEXT    NOT NULL,
	description  TEXT            ,
	industry     TEXT    NOT NULL,
	country      TEXT    NOT NULL,
	revenue      INTEGER NOT NULL,
	profits      INTEGER NOT NULL,
	assets       INTEGER NOT NULL,
	market_value INTEGER NOT NULL
);
"""
]


def connect(database="database.sqlite", mode="rw"):
	return contextlib.closing(sqlite3.connect(f"file:{database}?mode={mode}", uri=True))


def _add_companies(con, cur):
	with open("companies.json", "r") as f:
		companies = json.load(f)
		for c in companies:
			try:
				desc = c["description"]
			except:
				desc = None
			name = c["organizationName"]
			industry = c["industry"]
			country = c["country"]
			revenue = c["revenue"]
			profits = c["profits"]
			assets = c["assets"]
			market_value = c["marketValue"]
			cur.execute("SELECT ifnull(max(id)+1, 0) FROM companies")
			company_id, = cur.fetchone()
			cur.execute("INSERT INTO companies VALUES(?,?,?,?,?,?,?,?,?)",
				(company_id, name, desc, industry, country, revenue, profits, assets, market_value))
		con.commit()


def main():
	with connect(mode="rwc") as con:
		cur = con.cursor()
		for st in statements:
			cur.execute(st)
		_add_companies(con, cur)


if __name__ == "__main__":
	main()
