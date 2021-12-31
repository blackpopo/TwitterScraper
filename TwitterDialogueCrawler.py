import argparse
from utils.read_secrets import return_secret
from urllib.parse import unquote
from utils.url_create import *
from utils.sqlite_tool import *
from time import sleep

secrets = return_secret()
headers = create_headers(secrets['BEARER_TOKEN'])

import re
def clean_text(text):
    text = re.sub(r"\s", "", text)
    return text


def insert_conversations(conversations, twitter_ids, author_ids, created_ats, connection):
    cursor = connection.cursor()
    conversation_tree_id = cursor.execute("select max(conversation_tree_id) from conversation").fetchone()[0]
    if conversation_tree_id is not None:
        conversation_tree_id = conversation_tree_id+ 1
    else:
        conversation_tree_id = 0
    for conversation_order, text, twitter_id, author_id, created_at in zip(range(len(conversations)), conversations, twitter_ids, author_ids, created_ats):
        if conversation_order >= 1:
            pre_twitter_id, pre_author_id = twitter_ids[conversation_order-1], author_ids[conversation_order-1]
        else:
            pre_twitter_id, pre_author_id = None, None
        if conversation_order >= 2:
            pre_pre_twitter_id, pre_pre_author_id = twitter_ids[conversation_order - 2], author_ids[conversation_order - 2]
        else:
            pre_pre_twitter_id, pre_pre_author_id = None, None
        if conversation_order == len(conversations) -1:
            is_last_conversation = 1
        else:
            is_last_conversation = 0
        cursor.execute("insert into conversation(twitter_id, conversation_tree_id, conversation_order, text, created_at,"
                       "author_id, pre_twitter_id, pre_author_id, pre_pre_twitter_id, pre_pre_author_id, is_last_conversation) "
                       "values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       [twitter_id, conversation_tree_id, conversation_order, clean_text(text), created_at,
                        author_id, pre_twitter_id, pre_author_id, pre_pre_twitter_id, pre_pre_author_id, is_last_conversation])


def extract_replys(word, search_json_data, connection, recursive=True):
    cursor = connection.cursor()
    for data in search_json_data['data']:
        if "referenced_tweets" in data and data["referenced_tweets"][0]["type"] == "replied_to" and data["in_reply_to_user_id"] != data["author_id"]:
            print("Reply Message!")
            print(clean_text(data["text"]))
            print('created at ' + utc2jst_iso(data['created_at']).isoformat()+ '\n')
            #reply の twitter id が存在し, 自身のtwitter idが存在しないと判定すれば追加。is last conversationの更新を行なう。存在しなければ、全ての会話を調べる。
            cursor.execute("select twitter_id, conversation_tree_id, conversation_order, pre_twitter_id, pre_author_id, is_last_conversation from conversation where twitter_id = (?) limit 1", [data["referenced_tweets"][0]["id"]])
            row = cursor.fetchone()
            if row is None:
                conversations = [unquote(clean_text(data["text"]), encoding='utf-8')]
                twitter_ids= [data["id"]]
                author_ids=[data["author_id"]]
                created_ats =[utc2jst_iso(data['created_at']).isoformat()]
                conversations, twitter_ids, author_ids, created_ats = recursive_crawler(data["referenced_tweets"][0]["id"], conversations, twitter_ids, author_ids, created_ats)
                if len(conversations) >= 3:
                    insert_conversations(conversations, twitter_ids, author_ids, created_ats, connection)
                    print('Conversations \n' + '\n'.join(conversations) + '\n')
            else:
                pre_twitter_id, conversation_tree_id, pre_conversation_order, pre_pre_twitter_id, pre_pre_author_id, is_last_conversation = row
                cur_twitter_id = cursor.execute("select twitter_id from conversation where twitter_id=(?)", [data['id']]).fetchone()[0]
                if cur_twitter_id is None:
                    if is_last_conversation == 1:
                        cursor.execute("update conversation set is_last_conversation=(?) where twitter_id=(?)", [0, pre_twitter_id])
                    pre_author_id = data["in_reply_to_user_id"]
                    created_at = utc2jst_iso(data['created_at']).isoformat()
                    cursor.execute("insert into conversation(twitter_id, conversation_tree_id, conversation_order, text, created_at,"
                                            "author_id, pre_twitter_id, pre_author_id, pre_pre_twitter_id, pre_pre_author_id, is_last_conversation) "
                                                "values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                            [data["id"], conversation_tree_id, pre_conversation_order + 1, clean_text(data["text"]), created_at,
                                            data['author_id'], pre_twitter_id, pre_author_id, pre_pre_twitter_id, pre_pre_author_id, 1])
                    print(f"Add Conversation \n {clean_text(data['text'])} \n")
        if recursive:
            cursor.execute('update log set oldest_created_at=? where search_word=?', [utc2jst_iso(data['created_at']).isoformat(), word])
        else:
            cursor.execute('update log set newest_created_at=? where search_word=?', [utc2jst_iso(data['created_at']).isoformat(), word])
    return search_json_data

#Todo replyとref の author id のチェック
def recursive_crawler(pre_twitter_id, conversations, twitter_ids, author_ids, created_ats):
    url, params = create_twitter_url(pre_twitter_id)
    json_response = connect_to_endpoint(url, headers, params)
    if 'errors' in json_response:
        print("Error response!\n")
        return conversations, twitter_ids, author_ids, created_ats
    data = json_response['data']
    conversations.insert(0, unquote(clean_text(data["text"]), encoding='utf-8'))
    twitter_ids.insert(0, data["id"])
    author_ids.insert(0, data["author_id"])
    created_ats.insert(0, utc2jst_iso(data['created_at']).isoformat())
    if "referenced_tweets" in data and data["referenced_tweets"][0]["type"] == "replied_to" and data["in_reply_to_user_id"] != data["author_id"]:
        return recursive_crawler(data["referenced_tweets"][0]["id"], conversations, twitter_ids, author_ids, created_ats)
    else:
        return conversations, twitter_ids, author_ids, created_ats

def get_search_words(file_path='./Known_words.txt'):
    with open(file_path, 'r', encoding='utf-8') as f:
        words = f.readlines()
        words = [word.rstrip('\n') for word in words if word.strip() != '']
    return words

def search(word, end_time, start_time, connection, recursive=True):
    next_token = None

    while True:
        # Check if max_count reached
        print("-------------------")
        # print("Token: ", next_token)
        url, params = create_search_url(word, end_time, start_time)
        json_response = connect_to_endpoint(url, headers, params, next_token)
        result_count = json_response['meta']['result_count']
        print(f'Return {result_count} Tweets')
        if result_count == 0:
            print('No Tweets returned...')
            break

        extract_replys(word, json_response, connection, recursive)

        if 'next_token' in json_response['meta']: #keyで検索
            # Save the token to use for next call
            next_token = json_response['meta']['next_token']
            # print("Next Token: ", next_token)
        else:
            break

        sleep(2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', default='twitter_scraper.db')
    parser.add_argument('--drop_table', default=True)
    parser.add_argument('--recursive', default=True)
    args = parser.parse_args()

    conn = sqlite3_initialization(drop_tabel=args.drop_table)
    words = get_search_words()
    while True:
        for word in words:
            print(f"Word : {word}")
            word, end_time, start_time, newest_created_at, oldest_created_at = extract_date(word, conn)
            print(f"End time {end_time}\nStart time {start_time}\nNewest Twitter Created @ {newest_created_at}\nOldest Twitter Created @ {oldest_created_at}")
            if args.recursive:
                search(word, oldest_created_at,  start_time - timedelta(days=1), conn, args.recursive)
                _end_time = start_time - timedelta(days=1)
                _start_time = start_time - timedelta(days=2)
                search(word, _end_time, _start_time, conn, args.recursive)
                conn.execute('update log set start_time=? where search_word=?', [(start_time - timedelta(days=2)).isoformat(), word])
            else:
                assert end_time.date() + timedelta(days=1) < datetime.today().date(), "Future Twitter scraping!"
                search(word, newest_created_at, end_time - timedelta(days=1), conn, args.recursive)
                _end_time = end_time + timedelta(days=1)
                _start_time = end_time
                search(word, _end_time, _start_time, conn,  args.recursive)
                conn.execute('update log set end_time=? where search_word=?', [(end_time + timedelta(days=1)).isoformat(), word])

# newest_create_at > end_time > start_time > oldest_created_at

if __name__=='__main__':
    main()