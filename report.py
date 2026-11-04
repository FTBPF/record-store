import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import pandas as pd
    import sqlalchemy as sa
    import marimo as mo
    import matplotlib.pyplot as plt

    engine = sa.create_engine('postgresql+psycopg://')
    return engine, mo, pd, sa


@app.cell(hide_code=True)
def _(engine, pd, sa):
    def query(sql, **params):
        """
        Run `sql`, with its `:name` parameters, and return a DataFrame.
        """
        with engine.connect() as conn:
            return pd.read_sql_query(sa.text(sql), conn, params=params)

    query('SELECT COUNT(*) AS n FROM invoice WHERE billing_country = :country', country='Brazil')
    return (query,)


@app.cell(hide_code=True)
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
    Sales Overview
    """)
    return


@app.cell(hide_code=True)
def _(query):
    query("""
    select
        sum(total) as revenue,
        count(*) as n_invoices,
        avg(total) as average_invoice_value
    from invoice
    """)
    return


@app.cell(hide_code=True)
def _(query):
    df = query("""
    select
        date_trunc('month', invoice_date) as month,
        sum(total) as revenue,
        sum(total) - lag(sum(total)) over (order by date_trunc('month', invoice_date)) as change 
    from invoice
    group by month
    order by month
    """)
    return (df,)


@app.cell(hide_code=True)
def _(df):
    df.plot(x="month", y="revenue", kind="bar", figsize=(15, 5), title="Monthly Revenue")
    return


@app.cell(hide_code=True)
def _(query):
    query("""
    select
    	date_trunc('year', invoice_date) as year,
    	sum(total) as revenue,
    	sum(total) - lag(sum(total)) over (order by date_trunc('year', invoice_date)) as change
    from invoice
    group by date_trunc('year', invoice_date)
    order by "year"
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    CUSTOMERS AND COUNTRIES
    """)
    return


@app.cell(hide_code=True)
def _(query):
    query("""with revenue_per_customer as (
    select
    		c.customer_id,
    		c.country ,
    		sum(i.total) as revenue
    	from customer c
    	join invoice i on i.customer_id = c.customer_id
    	group by c.customer_id 
    )
    select
    	country,
    	sum(revenue) as total_revenue,
    	round(avg(revenue), 2) as revenue_per_customer_per_country
    from revenue_per_customer
    group by country
    order by total_revenue desc
    limit 5
    """)
    return


@app.cell(hide_code=True)
def _(query):
    query("""
    select
        i.customer_id,
        e.first_name || ' ' || e.last_name as employee_name,
        sum(i.total) as total_spent
    from invoice i
    join customer c on c.customer_id = i.customer_id
    join employee e on e.employee_id = c.support_rep_id
    group by i.customer_id, e.first_name, e.last_name 
    order by total_spent desc
    limit 10
    """)
    return


@app.cell(hide_code=True)
def _(query):
    query("""
    with customer_stats as (	
    	select
    		i.customer_id,
    		count(*) as n_invoice,
    		sum(i.total) as total_spent
    	from invoice i
    	group by i.customer_id
    ),
    categorized_customers as (
    	select 
    		cs.customer_id,
    		cs.total_spent,
    		case
    			when cs.n_invoice = 1 then 'One-time customer'
    			when cs.n_invoice >= 2 then 'Repeat customer'
    		end as customer_type
    	from customer_stats cs
    )
    select 
    	cc.customer_type,
    	count(cc.customer_id) as n_customers,
    	sum(cc.total_spent) as total_revenue,
    	100.0 * sum(cc.total_spent) / sum(sum(cc.total_spent)) over () as revenue_share_pct
    from categorized_customers cc
    group by cc.customer_type 
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


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
