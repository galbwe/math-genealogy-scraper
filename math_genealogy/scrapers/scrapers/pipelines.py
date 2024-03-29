# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json
import logging
import datetime

from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from math_genealogy.config import CONFIG
from math_genealogy.backend.db import Mathematician, StudentAdvisor, ArxivPaper


logger = logging.getLogger(__name__)


class SampleJsonWriterPipeline:
    def open_spider(self, spider):
        date = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        self.processed_ids = set()
        self.file = open(f"data/math_genealogy/mathematicians-{date}.json", "w")
        self.file.write('{"mathematicians": [\n')

    def close_spider(self, spider):
        self.file.write("]}")
        self.file.close()

    def process_item(self, item, spider):
        if item.id_ in self.processed_ids:
            raise DropItem(f'Already processed item with id "{item.id_}"')
        self.processed_ids.add(item.id_)
        self.file.write(json.dumps(ItemAdapter(item).asdict(), default=str) + ",\n")
        return item


class SqlalchemyWriterPipeline:

    batch_size = 250
    cache_size = 2000

    def open_spider(self, spider):
        self.skip = spider.name != "math_genealogy"
        self.processed_ids = set()
        self.items = []

        self.engine = create_engine(CONFIG.db_connection)
        self.Session = sessionmaker(bind=self.engine)

    def process_item(self, item, spider):
        if self.skip:
            return item
        self._update_cache()
        if not item.id_:
            raise DropItem("Item had invalid key")
        if item.id_ in self.processed_ids:
            raise DropItem(f'Already processed item with id "{item.id_}"')
        self.processed_ids.add(item.id_)
        item = self._clean_item(item)
        self.items.append(ItemAdapter(item).asdict())
        if len(self.items) >= self.batch_size:
            self._insert_items()
            self.items = []
        return item

    def _clean_item(self, item):
        item.id_ = int(item.id_)
        item.advisor_ids = [int(id_) for id_ in item.advisor_ids]
        item.student_ids = [int(id_) for id_ in item.student_ids]
        return item

    def _insert_items(self):
        session = self.Session()
        try:
            for item in self.items:
                mathematician = (
                    session.query(Mathematician).filter(Mathematician.id == item["id_"]).first()
                )
                if not mathematician:
                    mathematician = Mathematician(
                        id=item["id_"],
                    )
                mathematician.id = item["id_"]
                mathematician.name = item.get("name")
                mathematician.school = item.get("school")
                mathematician.graduated = item.get("graduated")
                mathematician.thesis = item.get("thesis")
                mathematician.country = item.get("nationality")
                mathematician.subject = item.get("subject")
                mathematician.math_genealogy_url = item.get("math_genealogy_url")
                mathematician.math_sci_net_url = item.get("math_sci_net_url")
                mathematician.publications = item.get("publications")
                mathematician.citations = item.get("citations")

                session.add(mathematician)

                for student_id in item.get("student_ids", []):
                    student = (
                        session.query(Mathematician).filter(Mathematician.id == student_id).first()
                    )
                    if not student:
                        student = Mathematician(
                            id=student_id,
                        )

                    session.add(student)

                    student_relation = (
                        session.query(StudentAdvisor)
                        .filter(
                            (StudentAdvisor.student_id == student_id)
                            & (StudentAdvisor.advisor_id == mathematician.id)
                        )
                        .first()
                    )
                    if not student_relation:
                        student_relation = StudentAdvisor()
                        student_relation.student_id = student.id
                        student_relation.advisor_id = mathematician.id

                    session.add(student_relation)

                for advisor_id in item.get("advisor_ids", []):
                    advisor = (
                        session.query(Mathematician).filter(Mathematician.id == advisor_id).first()
                    )
                    if not advisor:
                        advisor = Mathematician(
                            id=advisor_id,
                        )

                    session.add(advisor)

                    advisor_relation = (
                        session.query(StudentAdvisor)
                        .filter(
                            (StudentAdvisor.student_id == mathematician.id)
                            & (StudentAdvisor.advisor_id == advisor_id)
                        )
                        .first()
                    )
                    if not advisor_relation:
                        advisor_relation = StudentAdvisor()
                        advisor_relation.student_id = mathematician.id
                        advisor_relation.advisor_id = advisor_id

                    session.add(advisor_relation)

            session.commit()
        except Exception as e:
            session.rollback()
            logger.error("Exception while saving items to database: %r", e)
            logger.error(
                "Could not write items to database: %r",
                ",".join(str(item["id_"]) for item in self.items),
            )
        finally:
            session.close()

    def _update_cache(self):
        if len(self.processed_ids) > self.cache_size:
            self.processed_ids = set()


class ArxivPaperWriterPipeline:

    batch_size = 500

    def open_spider(self, spider):
        self.skip = spider.name != "arxiv"
        self.items = []
        self.engine = create_engine(CONFIG.db_connection)
        self.Session = sessionmaker(bind=self.engine)

    def process_item(self, item, spider):
        if self.skip:
            return item
        self.items.append(ItemAdapter(item).asdict())
        if len(self.items) >= self.batch_size:
            self._insert_items()
            self.items = []
        return item

    def _insert_items(self):
        session = self.Session()
        try:
            session.bulk_save_objects([
                ArxivPaper(
                    title=item['title'],
                    subjects=item['subjects'],
                    msc_classes=item['msc_classes'],
                )
                for item in self.items
            ])
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error("Exception while saving items to database: %r", e)
            logger.error(
                "Could not write items to database: %r",
                ",".join(str(item["id_"]) for item in self.items),
            )
        finally:
            session.close()
