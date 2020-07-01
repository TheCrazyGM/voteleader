import json
import math
from datetime import datetime, timedelta, timezone
from pprint import pprint

import dataset
import requests
from beem import Hive
from beem.account import Account
from beem.blockchain import Blockchain
from beem.comment import Comment
from beem.utils import construct_authorperm

hive = Hive(node='https://anyx.io')
blockchain = Blockchain(blockchain_instance=hive)
stream = blockchain.stream(
    opNames=['comment'], raw_ops=False, threading=True, thread_num=4)

db = dataset.connect('sqlite:///holybread.db')


def tally(author):
    today = datetime.now(timezone.utc)
    one_week = today - timedelta(days=7)
    count = 1
    acc = Account(author, blockchain_instance=hive)
    blog = acc.get_blog()
    for post in blog:
        if post['created'] >= one_week:
            count = count + 1
    return count


def create_db():
    uri = 'https://holybread.io/leaderboard_api/'
    payload = {'type': 'leaderboard', 'amount': 500}
    r = requests.get(uri, data=json.dumps(payload))
    json_repsonse = r.json()
    table = db.create_table("leaderboard", primary_id="rank")
    table.drop()

    for player in json_repsonse:
        table.insert(dict(user=player))
    table.create_index('user')
    db.commit()


def monitor():
    table = db.load_table('leaderboard')
    print("[Starting up...]")
    # Read the live stream and filter out only transfers
    for post in stream:
        try:
            q = table.find_one(user=post['author'])
            if q is not None:
                if post['author'] == q['user']:
                    perm = construct_authorperm(
                        post['author'], post['permlink'])
                    c = Comment(perm, blockchain_instance=hive)
                    if c.is_main_post():
                        print(f"[Post Found! By: {q['user']} Rank: {q['rank']}]")
                        vote_weight = math.ceil(((150 - q['rank'])*3.3) / (tally(post['author'])))
                        print(f"[{perm} -  Should be voted with a {vote_weight}% upvote.]")
        except Exception as e:
            print(f'[Error: {e}]')


def testing():
    table = db.load_table('leaderboard')
    q = table.find_one(rank=1)
    print(q)


if __name__ == "__main__":
    create_db()
    # testing()
    monitor()
