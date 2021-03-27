# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json
import datetime

from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem


class SampleJsonWriterPipeline:

    def open_spider(self, spider):
        date = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        self.processed_ids = set()
        self.file = open(f'data/math_genealogy/mathematicians-{date}.json', 'w')
        self.file.write('{"mathematicians": [\n')

    def close_spider(self, spider):
        self.file.write(']}')
        self.file.close()

    def process_item(self, item, spider):
        if item.id_ in self.processed_ids:
            raise DropItem(f'Already processed item with id "{item.id_}"')
        self.processed_ids.add(item.id_)
        self.file.write(
            json.dumps(
                ItemAdapter(item).asdict(),
                default=str) + ",\n")
        return item
