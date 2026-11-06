import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Executive Summary

    ## This report analyses the record store's sales, customer base, and catalogue performance using the Chinook database.

        Key Findings:
            * Sales Overview:
                The store has sold 412 tracks over the years, generating $2328,6 in total revenue.
                Looking at the revenue month by month and year by year it can be observed that the revenue is constant,
                    even tho there can also be seen some spikes and dips.

            * Customers & Countries:
                Revenue is concentrated in a handful of countries, and a small group of top-spending customers accounts for a
                    disproportionate share of sales.
                Repeat customers bring in all the revenue, which says something about where the store's loyalty and its growth
                    opportunity lies.
                Rock is the most bought genre from each country with the exception of Sweden who prefer Latin.

            * Catalogue:
                A few genres and artists drive most of the sales, while some albums have never sold a single track.

            * Sales Team:
                Revenue per support rep shifts from year to year, with different reps leading in different years and that shows

                    that every rep has a similiar revenue amount brought to the store.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Sales Overview
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### This table shows the total revenue of the store, the number of invoices made and the average invoice amount.
    """)
    return


@app.cell(hide_code=True)
def _(query):
    query("""
    select
        round(sum(total), 2) as revenue,
        count(*) as n_invoices,
        round(avg(total), 2) as average_invoice_value
    from invoice
    """).rename(columns={"revenue": "Total Revenue","n_invoices": "Number of Invoices", "average_invoice_value": "Average Invoice Value"})
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### This bar chart shows the monthly revenue per month up until the selected month and year below.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    import calendar

    year_var = mo.ui.dropdown(
        options=["2021", "2022", "2023", "2024", "2025"],
        value="2025",
        label="Year: "
    )

    month_var = mo.ui.dropdown(
        options={calendar.month_name[i]: i for i in range(1, 13)},
        value="December",
        label="Month: "
    )

    mo.md(f"Show data up to: {month_var} {year_var}")
    return calendar, month_var, year_var


@app.cell(hide_code=True)
def _(calendar, month_var, query, year_var):
    selected_year = int(year_var.value)
    selected_month = month_var.value

    last_day = calendar.monthrange(selected_year, selected_month)[1]

    target_date = f"{selected_year}-{selected_month:02d}-{last_day}"

    query("""
    select
        date_trunc('month', invoice_date) as month,
        sum(total) as revenue,
        sum(total) - lag(sum(total)) over (order by date_trunc('month', invoice_date)) as change 
    from invoice
    where invoice_date <= cast(:variable as date)
    group by month
    order by month
    """, variable=target_date
    ).plot(x="month", y="revenue", kind="bar", figsize=(15, 5), title="Monthly Revenue")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### This table shows the yearly revenue of the store and the growth in revenue
    """)
    return


@app.cell(hide_code=True)
def _(query):
    query("""
    select
    	extract(year from invoice_date) as year,
    	sum(total) as revenue,
    	sum(total) - lag(sum(total)) over (order by extract(year from invoice_date)) as change
    from invoice
    group by year
    order by "year"
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # CUSTOMERS AND COUNTRIES
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### This table shows the most bought genre from each country.
    """)
    return


@app.cell(hide_code=True)
def _(query):
    query("""
    with country_genre_sales as (
    	select
    		c.country ,
    		g."name" as genre ,
    		sum(il.quantity) as n_tracks_sold ,
    		round(sum(i.total), 2) as total_revenue ,
    		row_number() over (
    			partition by c.country
    			order by sum(il.quantity) desc
    		) as rn
    	from customer c 
    	join invoice i on i.customer_id = c.customer_id
    	join invoice_line il on il.invoice_id = i.invoice_id
    	join track t on t.track_id = il.track_id
    	join genre g on g.genre_id = t.genre_id
    	group by c.country , g."name"
    )
    select 
    	cgs.country ,
    	cgs.genre ,
    	cgs.n_tracks_sold ,
    	cgs.total_revenue 
    from country_genre_sales cgs
    where cgs.rn = 1
    order by cgs.n_tracks_sold desc
    """).rename(columns={"n_tracks_sold": "Number of Tracks Sold"})
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### This table shows the Revenue per country and the average revenue per customer in each country.
    """)
    return


@app.cell(hide_code=True)
def _(query):
    query("""
    with revenue_per_customer as (
        select
    		c.customer_id,
    		c.country ,
    		round(sum(i.total), 2) as revenue
    	from customer c
    	join invoice i on i.customer_id = c.customer_id
    	group by c.customer_id 
    )
    select
    	country,
    	round(sum(revenue), 2) as total_revenue,
    	round(avg(revenue), 2) as revenue_per_customer_per_country
    from revenue_per_customer
    group by country
    order by total_revenue desc
    limit 5
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    limit_customers = mo.ui.slider(
        start=1, 
        stop=50, 
        step=1, 
        value=10, 
        label="Number of customers to show: "
    )
    return (limit_customers,)


@app.cell(hide_code=True)
def _(limit_customers, mo):
    mo.vstack([
        mo.md(f"### This table shows the top {limit_customers.value} customers who spent the most money and their employee's name."),
        limit_customers
    ])
    return


@app.cell(hide_code=True)
def _(limit_customers, query):
    query("""
    select
        c.first_name || ' ' || c.last_name as customer_name,
        e.first_name || ' ' || e.last_name as employee_name,
        round(sum(i.total), 2) as total_spent
    from invoice i
    join customer c on c.customer_id = i.customer_id
    join employee e on e.employee_id = c.support_rep_id
    group by c.first_name, c.last_name, e.first_name, e.last_name 
    order by total_spent desc
    limit :n_customers
    """, n_customers=limit_customers.value
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### This table shows the number of one-time and repeated customers, their total revenue and share percentage.
    """)
    return


@app.cell(hide_code=True)
def _(query):
    query("""
    with customer_types as (
    	select 'One-time customer' as customer_type
    	union all
    	select 'Repeat customer' as customer_type
    ),
    customer_stats as (	
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
    	ct.customer_type,
    	count(cc.customer_id) as n_customers,
    	coalesce(round(sum(cc.total_spent), 2), 0) as total_revenue,
    	coalesce(round(100.0 * sum(cc.total_spent) / sum(sum(cc.total_spent)) over (), 2), 0) as revenue_share_pct
    from customer_types ct
    left join categorized_customers cc on ct.customer_type = cc.customer_type 
    group by ct.customer_type 
    """).rename(columns={"n_customers": "Number of Customers", "revenue_share_pct": "Revenue Share Percentage"})
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # CATALOGUE
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### This table shows the revenue per genre and the number of tracks sold.
    """)
    return


@app.cell(hide_code=True)
def _(query):
    query("""
    select
    	g."name",
    	round(sum(il.unit_price * il.quantity), 2) as revenue,
    	sum(il.quantity) as n_tracks
    from invoice_line il
    join track t on t.track_id = il.track_id 
    join genre g on g.genre_id = t.genre_id 
    group by g.genre_id   
    order by revenue desc
    """).rename(columns={"name": "Genre", "n_tracks": "Number of Tracks Sold"})
    return


@app.cell(hide_code=True)
def _(mo):
    limit_artists = mo.ui.slider(
        start=1, 
        stop=50, 
        step=1, 
        value=10, 
        label="Number of artists to show: "
    )
    return (limit_artists,)


@app.cell(hide_code=True)
def _(limit_artists, mo):
    mo.vstack([
        mo.md(f"### This table shows the top {limit_artists.value} best selling artists."),
        limit_artists
    ])
    return


@app.cell(hide_code=True)
def _(limit_artists, query):
    query("""
    select 
    	a2."name" ,
    	sum(il.unit_price * il.quantity) as revenue
    from track t
    join album a on t.album_id = a.album_id 
    join artist a2 on a2.artist_id = a.artist_id
    join invoice_line il on il.track_id = t.track_id
    group by a2."name" 
    order by revenue desc
    limit :n_artists
    """, n_artists=limit_artists.value
    ).rename(columns={"name": "Artists"})
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### This table shows artists that never sold a single track and that track's name.
    """)
    return


@app.cell(hide_code=True)
def _(query):
    query("""
    select 
    	a."name",
    	a2.title
    from artist a
    join album a2 on a2.artist_id = a.artist_id 
    left join (
    	select distinct t.album_id
    	from track t
    	join invoice_line il on il.track_id = t.track_id 
    ) sold_albums on a2.album_id = sold_albums.album_id 
    where sold_albums.album_id is null
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### This table shows the best selling track of each genre and the revenue each track made.
    """)
    return


@app.cell(hide_code=True)
def _(query):
    query("""
    with ranked_genre_titles as (
    	select
    		g."name" as genre,
    		t."name" as track_name,
    		sum(il.quantity * il.unit_price ) as total_revenue,
    		row_number() over (partition by t.genre_id order by sum(il.quantity * il.unit_price) desc) as rn
    	from genre g
    	join track t on t.genre_id = g.genre_id 
    	join invoice_line il on il.track_id = t.track_id 
    	group by t.genre_id, g."name" , t."name" 
    )
    select rgt.genre, rgt.track_name, rgt.total_revenue 
    from ranked_genre_titles rgt
    where rn = 1
    order by rgt.total_revenue desc
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # SALES TEAM
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### This table shows the revenue per support rep per year.
    """)
    return


@app.cell(hide_code=True)
def _(query):
    query("""
    with rep_yearly_revenue as (
    	select
    		e.employee_id,
    		e.first_name || ' ' || e.last_name as support_rep_name,
    		extract(year from i.invoice_date) as sales_year,
    		sum(i.total) as total_revenue
    	from invoice i
    	join customer c on c.customer_id = i.customer_id 
    	join employee e on e.employee_id = c.support_rep_id 
    	group by e.employee_id, support_rep_name, extract(year from i.invoice_date)
    )
    select 
    	ryr.support_rep_name,
    	ryr.sales_year,
    	ryr.total_revenue,
    	dense_rank() over (
    		partition by ryr.sales_year
    		order by ryr.total_revenue desc
    	) as rank_per_year
    from rep_yearly_revenue ryr
    order by ryr.sales_year, rank_per_year
    """)
    return


@app.cell(hide_code=True)
def _():
    import pandas as pd
    import sqlalchemy as sa
    import marimo as mo
    import matplotlib.pyplot as plt

    return mo, pd, sa


@app.cell(hide_code=True)
def _(sa):
    engine = sa.create_engine('postgresql+psycopg://')
    return (engine,)


@app.cell(hide_code=True)
def _(engine, pd, sa):
    def query(sql, **params):
        """
        Run `sql`, with its `:name` parameters, and return a DataFrame.
        """
        with engine.connect() as conn:
            return pd.read_sql_query(sa.text(sql), conn, params=params)

    return (query,)


@app.cell(hide_code=True)
def _(query):
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
    return


if __name__ == "__main__":
    app.run()
