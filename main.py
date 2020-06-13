from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess
from game_crawler.nba_crawler import NBASpider

# TODO read game ids by date in docker volume
# TODO add flags to specify date range

if __name__ == "__main__":
    print(__name__)
    settings = get_project_settings()
    settings["COOKIES_ENABLED"] = False
    settings["DOWNLOAD_DELAY"] = 1
    settings["ITEM_PIPELINES"] = {
        "game_crawler.pipelines.JsonWriterPipeline": 100,
        "game_crawler.pipelines.DBWriterPipeline": 100,
    }

    process = CrawlerProcess(settings)

    process.crawl(NBASpider, ids=["401071116", "401160654"])
    process.start()
