import json
import time
from datetime import datetime

import dataset
import requests
import schedule

from voteleader import db


def update_db():
    uri = 'https://holybread.io/leaderboard_api/'
    payload = {'type': 'leaderboard', 'amount': 160}
    r = requests.get(uri, data=json.dumps(payload))
    json_repsonse = r.json()
    table = db.create_table("leaderboard", primary_id="rank")
    table.drop()

    for player in json_repsonse:
        table.insert(dict(user=player))
    table.create_index('user')
    print(f'[Leaderboard Database updated at {datetime.now()}]')
    db.commit()


schedule.every(3).hours.do(update_db)


if __name__ == "__main__":
    print(f"[Clock Starting up...]")
    update_db()
    while True:
        schedule.run_pending()
        time.sleep(1)
