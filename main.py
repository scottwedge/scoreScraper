from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess
from game_crawler.nba_crawler import NBASpider
import os
import json
# TODO read game ids by date in docker volume
# TODO add flags to specify date range

def get_ids():
    fp = '/c/Users/ainig/Desktop/gameid_data/game_ids2'
    files = os.listdir(fp)

    ids = []
    for f in files:
        file_path = os.path.join(fp, f)
        if os.path.isfile(file_path):
            with open(os.path.join(fp, f)) as js:
                ids.extend(json.load(js))
    return ids

if __name__ == "__main__":
    ids = get_ids()
    settings = get_project_settings()
    settings["COOKIES_ENABLED"] = False
    settings["DOWNLOAD_DELAY"] = 2
    settings["LOG_LEVEL"] = "ERROR"
    settings["ITEM_PIPELINES"] = {
        "game_crawler.pipelines.JsonWriterPipeline": 100,
        "game_crawler.pipelines.DBWriterPipeline": 100,
    }

    process = CrawlerProcess(settings)

    process.crawl(NBASpider, ids = ids)
    process.start()
