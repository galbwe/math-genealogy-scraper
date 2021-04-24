import pdb
import re
from dataclasses import dataclass
from typing import Optional

import scrapy


@dataclass
class ArxivPaper:
    title: Optional[str] = None
    subjects: Optional[str] = None
    msc_classes: Optional[str] = None


PAPERS_PER_YEAR = 10500  # number of papers to scrape from each year

YEARS = list(range(11, 12))  # years 2010-2019

SHOW = 500  # number of papers to grab per page


class ArxivPaperSpider(scrapy.Spider):
    name = "arxiv"

    start_urls = [
        f"https://export.arxiv.org/list/math/{year}?skip={i}&show={SHOW}"
        for year in YEARS
        for i in range(0, PAPERS_PER_YEAR, SHOW)
    ]

    def parse(self, response):
        dt_elements = response.css('dt')
        dd_elements = response.css('dd')
        for dt_element, dd_element in zip(dt_elements, dd_elements):

            arxiv_paper = ArxivPaper()

            arxiv_paper.title = dd_element.css('.list-title::text')[-1].get().strip()

            primary_subject = dd_element.css(".list-subjects > .primary-subject::text").get()
            other_subjects = dd_element.css(".list-subjects::text")[-1].get()
            other_subjects = other_subjects.strip().split('; ')[1:]
            arxiv_paper.subjects = ', '.join([primary_subject, *other_subjects])

            abstract_a_tag = dt_element.css('a[title="Abstract"]').get()
            if abstract_a_tag:
                abstract_url_match = re.search(r'href="(\S+)"', abstract_a_tag)
                abstract_url = abstract_url_match.group(1) if abstract_url_match else None
                if abstract_url:
                    request = scrapy.Request(
                        "https://export.arxiv.org" + abstract_url,
                        callback=self.parse_abstract
                    )
                    request.meta['arxiv_paper'] = arxiv_paper
                    yield request
                else:
                    yield arxiv_paper
            else:
                yield arxiv_paper

    def parse_abstract(self, response):
        arxiv_paper = response.meta['arxiv_paper']
        arxiv_paper.msc_classes = response.css('.msc-classes::text').get()
        yield arxiv_paper
