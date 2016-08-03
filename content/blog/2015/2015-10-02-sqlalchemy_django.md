Title: SQLAlchemy queries in Django
Date: 2015-10-02
Category: web, backend, django
Slug: sql-alchemy-queries-in-django
Summary: Let's look at a simple way to run SQLAlchemy queries inside Django's request/response cycle.

Django's ORM is great for 99% of the common web development use cases. Every now and then, however, a bit more flexibility would go a long way and help stay out of the raw SQL rabbit hole. For example, reporting queries are difficult to build with Django's API and could benefit from a little more abstraction.

In this respect, I believe that SQLAlchemy's [SQL Expression Engine](http://docs.sqlalchemy.org/en/latest/core/tutorial.html) allows for significant flexibility with neat and reusable code. In this piece, we will look at how to write queries with the Expression Engine and have them executed by Django's DB engine without additional configuration.

## Integrating Django and SQLAlchemy

The great [aldjemy](https://github.com/Deepwalker/aldjemy) package makes the initial integration painless, and sets up SQLAlchemy to reuse Django's DB connection.

However, its README focuses on on ORM-style queries using SQLAlchemy's own ORM API. Instead, let's look at how to extract the table information to run our own queries built using the expression engine.

    from aldjemy.core import get_tables, get_engine
    from sqlalchemy.sql import select

    # for the default DB
    engine = get_engine()
    # for another DB
    engine = get_engine('tracking')
    
    # a dict with DB tables
    tables = get_tables()

    # each table can now be accessed to build queries:
    widgets = tables['widgets']

    query = select([
                widget.c.id,
                widget.c.name])

## Running the query

Since the `engine` object is already available, we can just open a connection and run the query:

    conn = engine.connect()
    result = conn.execute(query)

As an added note, I've found [Pandas](http://pandas.pydata.org) to be very useful in these kinds of situations. In fact, easy column and row-level operations at the Python level nicely complement the flexibility in data retrieval afforded by SQLAlchemy.

When using Pandas, fetching the query results into a DataFrame is even easier:

    data_frame = pandas.read_sql_query(query, engine)

## Under the hood

While Django doesn't support connection pooling, it obviously has its own transaction system which is syncronized with the request/response cycle. Aldjemy plugs into this with the `core.DjangoPool` class which operates as a SQLAlchemy `NullPool` that piggybacks on Django's connections. Each connection is wrapped in a `wrapper.Wrapper` to disable SQLAlchemy's handling of transactions and rely on Django's.

Tables are generated through reflection of Django's models in the `tables.generate_tables` function. Aldjemy keeps a mapping of Django field types to SQLAlchemy types and iterates through each model to add the relevant columns to its table.

## Conclusions

We have seen how to use SQLAlchemy's SQL Expression Language to run complex queries on Django's database without needing to create additional connections or manually define the database schema.