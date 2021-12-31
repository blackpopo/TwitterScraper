import sqlite3
import argparse
from datetime import datetime

def get_connection(db='twitter_scraper.db'):
    connection = sqlite3.connect(db)
    return connection

def get_max_conversation_tree_id(conn):
    cursor = conn.cursor()
    max_conversation_tree_id = cursor.execute("select max(conversation_tree_id) from conversation").fetchone()[0]
    return max_conversation_tree_id

def get_conversation_tree(tree_id, conn):
    cursor = conn.cursor()
    conversation_dict = dict()
    cursor.execute("select * from conversation where conversation_tree_id = (?)", [tree_id])
    conversation_tree =  sorted(cursor.fetchall(), key=lambda x: x[2], reverse=True)
    last_conversation_ids = list()
    for row in conversation_tree:
        conversation_dict[row[0]] = row[1:]
        if row[-1] == 1:
            last_conversation_ids.append(row[0])
    assert len(last_conversation_ids) > 0
    return conversation_dict, last_conversation_ids

def get_dialogue(conversation_tree, last_conversation_ids):
    res_dialogues = list()
    print(last_conversation_ids)
    for id in last_conversation_ids:
        statement = conversation_tree[id]
        pre_twitter_id = statement[5]
        author_id = statement[4]
        pre_pre_author_id = statement[8]
        if author_id == pre_pre_author_id:
            dialogues = [statement[2]]
            res_dialogues.append(recursive_dialogue(dialogues, conversation_tree, pre_twitter_id, False))
    return res_dialogues

def recursive_dialogue(dialogues, conversation_tree, pre_twitter_id, return_flag):
    statement = conversation_tree[pre_twitter_id]
    pre_twitter_id = statement[5]
    utterance = statement[2]
    dialogues.insert(0, utterance)
    author_id = statement[4]
    pre_pre_author_id = statement[8]
    if return_flag:
        return dialogues
    elif author_id != pre_pre_author_id:
        return recursive_dialogue(dialogues, conversation_tree, pre_twitter_id, True)
    elif author_id == pre_pre_author_id:
        return recursive_dialogue(dialogues, conversation_tree, pre_twitter_id, False)


def get_conversation(conversation_tree, last_conversation_ids):
    res_conversations = list()
    for id in last_conversation_ids:
        statement = conversation_tree[id]
        pre_twitter_id = statement[5]
        conversations = [statement[2]]
        res_conversations.append(recursive_conversation(conversations, conversation_tree, pre_twitter_id))
    return res_conversations

def recursive_conversation(conversations, conversation_tree, pre_twitter_id):
    statement = conversation_tree[pre_twitter_id]
    pre_twitter_id = statement[5]
    utterance = statement[2]
    conversations.insert(0, utterance)
    if pre_twitter_id is None: #pre_twitter_id is None
        return conversations
    else:
        return recursive_conversation(conversations, conversation_tree, pre_twitter_id)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--type', default='conversation')
    args = parser.parse_args()
    type = args.type
    assert type=='conversation' or type=='dialogue', 'data extraction type must be `conversation` or `dialogue`'
    conn = get_connection()
    conversation_tree_id = get_max_conversation_tree_id(conn) + 1
    save_list = list()
    for tree_id in range(conversation_tree_id):
        conversation_tree, conversation_count = get_conversation_tree(tree_id, conn)
        if type == 'conversation':
            conversation = get_conversation(conversation_tree, conversation_count)
            save_list.append(conversation)
        else:
            dialogue= get_dialogue(conversation_tree, conversation_count)
            save_list.append(dialogue)
    save_list = ['\n'.join(item) for l in save_list for item in l]
    with open(type + '_' + datetime.now().strftime('%Y-%m-%d_%H%M%S') + '.txt', 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(save_list))

if __name__=='__main__':
    main()
