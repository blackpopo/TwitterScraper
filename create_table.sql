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

create table  if not exists log(
    search_word text unique NOT NULL,
    start_time text NOT NULL,
    end_time text NOT NULL,
    newest_created_at text NOT NULL,
    oldest_created_at text NOT NULL
)

-- import sqlite3
--
-- # ユーザ定義型 その1
-- # データベース内部ではセミコロン区切りのテキストになっている、。区切り文字は変更してもいい
-- sqlite3.register_adapter(list, lambda l: ';'.join([str(i) for i in l]))
-- sqlite3.register_converter('LIST', lambda s: [item.decode('utf-8')  for i in s.split(bytes(b';'))])
--
-- # ユーザ定義型 その2
-- sqlite3.register_adapter(bool, lambda b: str(b))
-- sqlite3.register_converter('BOOL', lambda l: bool(eval(l)))