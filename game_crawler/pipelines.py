import json
import scrapy
from db import nba
import os

# TODO add SQL Pipeline instead

USER = os.environ["dbName"]
PASSWORD = os.environ["dbPass"]


class DBWriterPipeline(object):
    def open_spider(self, spider):
        self.db = nba.nbaDB(USER, PASSWORD)

    def close_spider(self, spider):
        # self.file.close()
        pass

    def process_item(self, item, spider):
        return item


class JsonWriterPipeline(object):
    def open_spider(self, spider):
        self.file = open("items.json", "w")

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item
