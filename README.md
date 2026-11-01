# Record Store Report

Produce a polished, presentation-quality Marimo notebook answering a
digital music store owner's business questions, with SQL doing the work,
against the Chinook database on PostgreSQL.

This is `quake-report`'s SQL sibling: same standard of narrative and
polish, but the analysis lives in queries, not in pandas.


## Learning Objectives

* Exploring an unfamiliar schema: tables, keys, and how they relate.
* Analytical SQL on a real (if small) business database: joins,
  aggregation, `HAVING`, subqueries, CTEs, window functions and dates
  (Sessions 1 to 3).
* Running parameterized SQL from a Marimo notebook, through SQLAlchemy,
  and bringing back only small results (Sessions 2, 5 and 6).
* Checking your own numbers: sanity checks, and the same answer two ways
  (SQL and pandas).
* Writing for a reader who doesn't read SQL.


## Concepts

* **Customer** — someone who buys tracks, each looked after by a sales
  **support rep** (an employee).
* **Invoice** — one purchase, by one customer, on one date, with one or more
  **invoice lines** (one track each, with its unit price and quantity).
* **Track** — a song, on an **album**, by an **artist**, with a **genre**
  and a **media type**.
* **Report** — the final notebook: framed sections, each answering one of
  the owner's questions.


## Data Source

[Chinook](https://github.com/lerocha/chinook-database) is a sample database
modelled on a digital music store, with ready-made scripts for many
engines. Download `Chinook_PostgreSql.sql` from the repository's
[latest release](https://github.com/lerocha/chinook-database/releases/latest).

Your database on the lab VM, `ff.record-store`, already exists, and is
empty. The script, however, starts by dropping and creating a database
called `chinook`, and connecting to it (`\c chinook`): you can't do that,
and don't need to. Remove those three lines, then load the rest into your
database.

Connect as in the sessions, with the libpq environment variables
(`PGHOST`, `PGUSER`, `PGPASSWORD`, ...), and point `PGDATABASE` at this
project's database:

```
export PGDATABASE=ff.record-store
psql -f ....sql
```

With those set, `psql` needs no connection options, and neither does
SQLAlchemy (see Guidance).

Before anything else, check what you got: `\dt` and `\d <table>` in
`psql`, or DBeaver's navigator. The PostgreSQL script uses snake_case names
(`invoice_line`, `invoice_id`); other Chinook versions don't, so if you use
one, use the names *your* copy has.

There's also an empty `ff.record-store-test` database. This project doesn't
need it, but it's yours to use: say, to try the load before doing it for
real.


## Objectives

Work through these roughly in order; each builds on the last.

1. **Explore**
   * Draw the ER diagram yourself (paper is fine): which tables, which
     keys, which relationships? Where does a sale's money come from?
   * An **ER (entity-relationship) diagram** is a picture of a database:
     one box per table (entity), listing its columns with the primary key
     marked, and one line per foreign key (relationship) between two
     boxes, showing which side is the "one" and which the "many" (one
     customer, many invoices).
   * Then compare yours with DBeaver's: in the Database Navigator, expand
     your connection down to `ff.record-store` → Schemas → `public`,
     right-click it, and choose *View Diagram*. Drawing it first is the
     point: that's how you learn the schema.
   * Count the rows in every table, and run a few sanity checks (see
     Acceptance).

2. **Sales overview**
   * Total revenue, number of invoices, average invoice value.
   * Revenue per month over the whole period, with month-over-month
     change (`LAG`), and as a bar chart.
   * Revenue per year: is the store growing?

3. **Customers and countries**
   * The 5 countries with the most revenue, with revenue per customer in
     each.
   * The top 10 customers by lifetime spend, with their support rep's name
     (a join through `employee`).
   * One-time vs. repeat customers: how many of each category, and what share of
     revenue each brings.

4. **Catalogue**
   * Revenue and tracks sold per genre. Do the two rankings differ?
   * The 10 best-selling artists.
   * Artists with albums that never sold a single track (anti-join).
   * The best-selling track of each genre (a window function, top 1 per
     group).

5. **Sales team**
   * Revenue per support rep per year, ranked within each year.
     Who improved most?

6. **Your own question**
   * Ask and answer one question the owner didn't think of.

7. **Narrative and polish**
   * An "Executive Summary" near the top, written *last*.
   * Every chart titled and labelled, with units; section headers that
     read like a report's table of contents.


## Guidance

* Set the project up with `uv init`, then
  `uv add marimo pandas sqlalchemy "psycopg[binary]"`, plus the charting
  library you used in `quake-report`.
* Connect with SQLAlchemy from the notebook's first cells, with an
  otherwise empty URL: `postgresql+psycopg://`. libpq fills in the host,
  user, password and database from the `PG*` variables, as it does for
  `psql`. Set them before starting Marimo:

  ```
  export PGDATABASE=ff.record-store
  uv run marimo edit report.py
  ```

* Query with Marimo SQL cells set to that engine, or with a small `query`
  helper (Session 6's B.3), which you'll want in every project from now on:

  ```python
  import pandas as pd
  import sqlalchemy as sa

  engine = sa.create_engine('postgresql+psycopg://')

  def query(sql, **params):
      """Run `sql`, with its `:name` parameters, and return a DataFrame."""
      with engine.connect() as conn:
          return pd.read_sql_query(sa.text(sql), conn, params=params)

  query('SELECT COUNT(*) AS n FROM invoice WHERE billing_country = :country',
        country='Brazil')
  ```

* Keep the queries in the notebook, readable: this is a SQL project, so the
  SQL is part of what a technical reader will look at.
* Any value that varies (a year, a country, a "top N") goes in as a
  parameter. Marimo UI elements (a year dropdown, say) are a nice way to
  show that off.
* Bring back small results. Aggregate in SQL; use pandas only to shape the
  result for a chart or a table.
* Do at least three of the questions **twice**: once in SQL, once in
  pandas from raw tables (`pd.read_sql_table`). The numbers must match;
  note in a sentence which version was clearer.
* Watch for fan-out: invoice totals vs. invoice line sums, and anything
  joined through `track` or `genre`.
* For the level of polish expected, look again at the example reports
  referenced in `quake-report`.


## Suggested Pace

One working week, at 4-6h a day. Each day ends with something concrete to
show at a check-in. Check-ins happen about twice a week, on days that
vary: whenever one comes, show where you are, and never wait for one to
carry on.

| Day | Focus | End of day |
|-----|-------|------------|
| 1 | **Explore.** Load Chinook, draw the ER diagram, count every table, write the Acceptance sanity checks. Notebook skeleton: connection, `query` helper, section headers. | ER diagram drawn and compared with DBeaver's; sanity checks pass. |
| 2 | **Sales and customers.** Objectives 2 and 3: totals, monthly revenue with `LAG` and a chart, countries, top customers with reps, one-time vs. repeat. | Seven or so answered questions, each with a rough one-line finding. |
| 3 | **Catalogue and team.** Objectives 4 and 5: genres, artists, never-sold albums, best track per genre, reps per year. | Every owner question answered, even if roughly. |
| 4 | **Twice and tidy.** Three questions redone in pandas, numbers matching. Your own question. Reorganize: parameters where values vary, charts labelled, headers like a table of contents. | "Run all" works top to bottom from a fresh kernel. |
| 5 | **Narrative.** Executive Summary, written last. Tighten every finding; hide code that doesn't serve the reader. Prepare a 10-minute presentation for the next check-in. | Committed, pushed, ready to present. |


## Stretch Goals

* A Marimo dropdown for the year (or the country) that re-runs the
  relevant queries.
* Playlist analysis: which playlists hold the most best-selling tracks?
* Run your three heaviest queries on DuckDB, attached to PostgreSQL
  (Session 6), and compare.


## Acceptance

Your notebook should let a reader answer, without reading your code:

* How much has the store sold, in total and per year? Is it growing?
* Which countries and which customers matter most?
* Which genres and artists sell, and which never do?
* How is the sales team doing?

Add a few `assert` sanity checks right after connecting, for example:

```python
# The total of the invoices equals the total of their lines.
totals = query('SELECT SUM(total) AS t FROM invoice')
lines = query('SELECT SUM(unit_price * quantity) AS t FROM invoice_line')
assert round(totals.t[0], 2) == round(lines.t[0], 2)

# Every invoice line points at an existing track (no orphans).
orphans = query('''
    SELECT COUNT(*) AS n
    FROM invoice_line AS il
    LEFT JOIN track AS t ON t.track_id = il.track_id
    WHERE t.track_id IS NULL
''')
assert orphans.n[0] == 0
```

The latest Chinook release (v1.4.5) has 59 customers, 412 invoices, 3503
tracks, 275 artists and 25 genres, with total sales of 2328.60, between
January 2009 and December 2013. If your copy differs, say so in the
notebook and use your numbers: the checks above are what matter.
