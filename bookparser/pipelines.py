# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
import re

MONGO_HOST = 'localhost'
MONGO_PORT = 27017
DB_NAME = 'books'


class BookparserPipeline:
    def __init__(self):
        self.client = MongoClient(host=MONGO_HOST, port=MONGO_PORT)
        self.db = self.client[DB_NAME]

    def process_item(self, item, spider):
        if spider.name == 'book24':
            item['domain'] = item['domain'][0]
            if item['rating']:
                item['rating'] = str(item['rating']).strip()
            for price in [item['price_old'], item['price_actual']]:
                if price:
                    match = re.fullmatch(
                        r'(\d+\s*\d+)\s*(\D+)', self.convert_str(price))
                    if match:
                        if item['price_old'] == price:
                            item['price_old'] = match.group(1).replace(' ', '')
                            item['currency_old'] = match.group(2).strip()
                        elif item['price_actual'] == price:
                            item['price_actual'] = match.group(1).replace(' ', '')
                            item['currency_actual'] = match.group(2).strip()
            collection = self.db[spider.name]
            collection.update_one({'link': item['link']}, {"$set": item},
                                  upsert=True)
        return item

    @staticmethod
    def convert_str(convert_object):
        conv_str = "".join(convert_object)
        return " ".join(re.findall(r'[.,–a-zA-Zа-яА-Я0-9$₽]+', conv_str))
