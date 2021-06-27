import math
import time
from datetime import datetime, timedelta, timezone

import requests
from beem import Hive
from beem.account import Account
from beem.blockchain import Blockchain
from beem.comment import Comment
from beem.utils import construct_authorperm

from voteleader import db, voter, wif


nodes_urls = [
    "https://api.hive.blog",
    "https://hived.privex.io",
]
hive = Hive(node=nodes_urls, keys=wif)
blockchain = Blockchain(blockchain_instance=hive)
stream = blockchain.stream(
    opNames=["comment"], raw_ops=False, threading=True, thread_num=4
)


def tally(author):
    today = datetime.now(timezone.utc)
    one_week = today - timedelta(days=7)
    acc = Account(author, blockchain_instance=hive)
    blog = acc.get_blog()
    return 1 + sum(post["created"] >= one_week for post in blog)


def monitor():
    table = db.load_table("leaderboard")
    vote_table = db["vote_history"]
    print("[Monitor Starting up...]")


def monitor():
    table = db.load_table("leaderboard")
    vote_table = db["vote_history"]
    print("[Monitor Starting up...]")
    # Read the live stream and filter out only transfers
    for post in stream:
        # print(post["block_num"])
        try:
            q = table.find_one(user=post["author"])
            if q is not None and post["author"] == q["user"]:
                perm = construct_authorperm(post["author"], post["permlink"])
                c = Comment(perm, blockchain_instance=hive)
                if c.is_main_post():
                    today = datetime.now(timezone.utc)
                    week_tally = tally(post["author"])
                    print(f"[Post Found! By: {q['user']} Rank: {q['rank']}]")
                    vote_weight = math.ceil(((65 - q["rank"]) * 2.5) / (week_tally))
                    vote_weight = 100 if vote_weight >= 100 else vote_weight
                    vote_weight = 1 if vote_weight <= 1 else vote_weight
                    print(
                        f"[{week_tally} post(s) a week. - {perm} should be voted with a {vote_weight}% upvote.]"
                    )
                    # Trying to catch about the mark for curation.
                    time.sleep(60)
                    tx = c.upvote(weight=vote_weight, voter=voter)
                    reply_body = f"Thank you for supporting Holybread and Thunkgaria over the last year! Enjoy your upvote -simplegame"
                    # print(tx)
                    reply_tx = c.reply(
                        reply_body, title="Leaderboard Vote", author=voter
                    )
                    # print(reply_tx)
                    vote_table.insert(
                        dict(
                            user=q["user"],
                            rank=q["rank"],
                            post=perm,
                            vote_weight=vote_weight,
                            vote_time=today,
                        )
                    )
        except Exception as e:
            print(f"[Error: {e}]")


if __name__ == "__main__":
    monitor()
