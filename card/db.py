import pymssql, sqlite3
from flask import current_app, g
import click, re
# این برنامه امکان اتصال به پایگاه داده برای ذخیره سازی اطلاعات را فراهم میکند

def connect(config):
    db = None
    if config['DATABASE_TYPE'] == 'sqlite':
        db = sqlite3.connect(
            config['SQLITE_PATH'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        db.row_factory = sqlite3.Row
    else:
        db = pymssql.connect(
            server=config['MSSQL_DATABASE_HOST'],
            port=config['MSSQL_DATABASE_PORT'],
            user=config['MSSQL_DATABASE_USERNAME'],
            password=config['MSSQL_DATABASE_PASSWORD'],
            database=config['MSSQL_DATABASE_NAME'],
            as_dict=True
        )
    return db

def get_db():
    if 'db' not in g:
        g.db = connect(current_app.config)

    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    if current_app.config['DATABASE_TYPE'] == 'sqlite':
        with current_app.open_resource('assets/schema-sqlite.sql') as f:
            db = get_db()
            db.executescript(f.read().decode('utf8'))
    else:
        with current_app.open_resource('assets/schema-mssql.sql') as f:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(f.read().decode('utf8'))
            conn.commit()
            cursor.close()

@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

def query_string(query):
    r = query
    if current_app.config["DATABASE_TYPE"] == "sqlite":
        r = query.replace("%s", "?")
        r = r.replace("%d", "?")
        r = re.sub(r'[TOPtop]{3}\(\d*\)', '', r)
    return r

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def get_conn_cursor():
    conn = get_db()
    cursor = conn.cursor()
    if current_app.config['DATABASE_TYPE'] == 'sqlite':
        cursor.row_factory = dict_factory
    return conn, cursor