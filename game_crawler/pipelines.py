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
        self.async_data = {}

    def close_spider(self, spider):
        self.db.session.commit()
        self.db.session.close()

    def process_item(self, item, spider):
        gid = item.get("game_id")
        fields = ["player_stats", "game", "team_stats"]

        if gid not in self.async_data:
            self.async_data[gid] = {}
        self.async_data[gid][item.get("type")] = item.get("data")

        if set(self.async_data[gid].keys()) == set(fields):
            self.db.add_record(self.async_data[gid])
            del self.async_data[gid]
            self.db.session.commit()
        return f"game{gid} processed"

class JsonWriterPipeline(object):
    def open_spider(self, spider):
        self.file = open("items.json", "w")

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item
