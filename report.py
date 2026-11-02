import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import pandas as pd
    import sqlalchemy as sa
    import marimo as mo

    engine = sa.create_engine('postgresql+psycopg://')
    return engine, mo, pd, sa


@app.cell
def _(engine, pd, sa):
    def query(sql, **params):
        """
        Run `sql`, with its `:name` parameters, and return a DataFrame.
        """
        with engine.connect() as conn:
            return pd.read_sql_query(sa.text(sql), conn, params=params)

    query('SELECT COUNT(*) AS n FROM invoice WHERE billing_country = :country', country='Brazil')
    return (query,)


@app.cell
def _(query):
    query("""
        SELECT
            (select count(*) from album) as album,
            (select count(*) from artist) as artist,
            (select count(*) from customer) as customer,
            (select count(*) from employee) as employee,
            (select count(*) from genre) as genre,
            (select count(*) from invoice) as invoice,
            (select count(*) from invoice_line) as invoice_line,
            (select count(*) from media_type) as media_type,
            (select count(*) from playlist) as playlist,
            (select count(*) from playlist_track) as playlist_track,
            (select count(*) from track) as track;
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ACCEPTANCE

    How much has the store sold, in total and per year? Is it growing?

    Which countries and which customers matter most?

    Which genres and artists sell, and which never do?

    How is the sales team doing?
    """)
    return


if __name__ == "__main__":
    app.run()
