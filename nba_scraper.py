from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess
from game_crawler.nba_crawler import NBASpider
from db import nba
import os
import json
import time
import random

# TODO read game ids by date in docker volume
# TODO add flags to specify date range

USER = os.environ["dbName"]
PASSWORD = os.environ["dbPass"]


def get_ids():
    fp = "/c/Users/ainig/Desktop/gameid_data/game_ids"
    files = os.listdir(fp)

    ids = []
    for f in files:
        file_path = os.path.join(fp, f)
        if os.path.isfile(file_path):
            with open(os.path.join(fp, f)) as js:
                ids.extend(json.load(js))
    return ids


if __name__ == "__main__":
    print("getting game ids")
    ids = get_ids()

    db = nba.nbaDB(USER, PASSWORD)

    # this step removes ids from the list to process if they have already been processed
    # required due to multiple runs/debug sessions to get it working properly.
    query = db.session.query(nba.Game.id)
    t = query.all()
    current_ids = [str(i[0]) for i in t]

    ids = [i for i in ids if i not in current_ids]
    del db

    print(f"{len(ids)} games found")

    settings = get_project_settings()
    settings["COOKIES_ENABLED"] = False
    settings["DOWNLOAD_DELAY"] = 1
    settings["LOG_LEVEL"] = "INFO"
    settings["ITEM_PIPELINES"] = {
        "game_crawler.pipelines.DBWriterPipeline": 100,
    }
    settings["AUTOTHROTTLE_ENABLED"] = True
    settings["AUTHROTTLE_TARGET_CONCURRENCY"] = 1

    process = CrawlerProcess(settings)
    process.crawl(NBASpider, ids=ids)
    print("starting crawler")
    process.start()
    print("crawling completed")
