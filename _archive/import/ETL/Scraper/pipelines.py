# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

# Everytime "yield" is called in bga_spiders.py this Pipeline is called.
from scrapy.exporters import JsonItemExporter
from scrapy.exporters import CsvItemExporter
from itemadapter import ItemAdapter
import json


class BgaPipeline:
    def open_spider(self, spider):
        self.file = open('../Data/BoardGameAtlas/Raw/Scrapy/Publishers/bga_boardGameRatings.json', 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(ItemAdapter(item).asdict()) + "\n"
        self.file.write(line)
        return item



