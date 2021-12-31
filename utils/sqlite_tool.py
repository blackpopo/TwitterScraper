import sqlite3

def sqlite3_initialization(db='twitter_scraper.db', drop_tabel=False):
    connection = sqlite3.connect(db, isolation_level=None)
    if drop_tabel:
        connection.execute("drop table conversation")
        connection.execute("drop table log")
    cursor = connection.cursor()
    cursor.execute("""
create table if not exists conversation(
  twitter_id text primary key NOT NULL, --key
  conversation_tree_id integer NOT NULL, --0
  conversation_order integer NOT NULL, --1
  text text NOT NULL, --2
  created_at text NOT NULL, --3
  author_id text NOT NULL, --4
  pre_twitter_id text, --5
  pre_author_id text, --6
  pre_pre_twitter_id text, --7
  pre_pre_author_id text, --8
  is_last_conversation integer NOT NULL --9
);
    """)
    cursor.execute("""
    create table  if not exists log(
    search_word text unique NOT NULL,
    start_time text NOT NULL,
    end_time text NOT NULL,
    newest_created_at text NOT NULL,
    oldest_created_at text NOT NULL
)
    """)
    return connection
