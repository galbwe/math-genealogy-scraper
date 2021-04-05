import random
import re
from typing import Optional, List, Tuple
from dataclasses import dataclass, field, asdict

import scrapy


@dataclass
class Mathematician:
    id_: Optional[int] = None
    name: Optional[str] = None
    school: Optional[str] = None
    graduated: Optional[str] = None
    thesis: Optional[str] = None
    nationality: Optional[str] = None
    subject: Optional[str] = None
    advisor_ids: List[int] = field(default_factory=list)
    student_ids: List[int] = field(default_factory=list)
    math_genealogy_url: Optional[str] = None
    math_sci_net_url: Optional[str] = None
    publications: Optional[int] = None
    citations: Optional[int] = None


class MathGenealogySpider(scrapy.Spider):
    name = "math_genealogy"

    start_urls = [
        f"https://www.mathgenealogy.org/id.php?id={i}"
        for i in random.sample(range(1, 265263 + 1), k=16)
    ]

    def parse(self, response):
        # instantiate data class
        mathematician = Mathematician()

        mathematician.math_genealogy_url = str(response.url)

        # get id
        id_match = re.search(r"id=(\d+)", response.url)
        if id_match is not None:
            mathematician.id_ = id_match.group(1)

        # get name
        name = response.css("h2::text").get()
        if name:
            mathematician.name = name.strip()

        # get school
        mathematician.school = response.css('span[style*="006633"]::text').get()

        # get year grauduated
        graduated_span = response.css('span[style="margin-right: 0.5em"]').get()
        if graduated_span:
            graduated_match = re.search(r"\D(\d{4})\D", graduated_span)
            if graduated_match:
                mathematician.graduated = int(graduated_match.group(1))

        # get thesis title
        mathematician.thesis = response.css("#thesisTitle::text").get()

        # get nationality
        nationality_img = response.css('img[src*="img/flags/"]').get()
        if nationality_img:
            title_match = re.search('title="(.+)"', nationality_img)
            if title_match:
                mathematician.nationality = title_match.group(1)

        # links to follow
        urls = []

        # get links and ids for other mathematicians on the page
        mathematician_a_selectors = response.css('a[href^="id.php?id="]')
        # remove link to students in chronological order
        mathematician_a_selectors = [
            s for s in mathematician_a_selectors if "Chrono=" not in s.get()
        ]
        # student links are inside a table, but advisor links are outside the table
        student_selectors = response.css('table a[href^="id.php?id="]')
        student_text = set(map(lambda x: x.get(), student_selectors))

        advisor_selectors = [s for s in mathematician_a_selectors if s.get() not in student_text]

        for advisor_selector in advisor_selectors:
            advisor_id, advisor_url = self.parse_a_selector(advisor_selector)
            mathematician.advisor_ids.append(advisor_id)
            urls.append(advisor_url)

        for student_selector in student_selectors:
            student_id, student_url = self.parse_a_selector(student_selector)
            mathematician.student_ids.append(student_id)
            urls.append(student_url)

        # get subject
        mathematician.subject = response.css(
            'div[style="text-align: center; margin-top: 1ex"]::text'
        ).get()

        # get link to MathSciNet if it exists
        math_sci_net_link = response.css('a[href^="http://www.ams.org/mathscinet/MRAuthorID"]')
        math_sci_net_a_tag = math_sci_net_link.get()
        if math_sci_net_a_tag:
            math_sci_net_url_match = re.search('href="(.+)"', math_sci_net_a_tag)
            if math_sci_net_url_match:
                mathematician.math_sci_net_url = math_sci_net_url_match.group(1)

        # follow math sci net url and try to scrape publications and citations
        if mathematician.math_sci_net_url:
            # follow valid url, passing data collected up to this point along to the next parse method
            request = scrapy.Request(
                mathematician.math_sci_net_url, callback=self.parse_math_sci_net
            )
            request.meta[
                "mathematician"
            ] = mathematician  # passes collected data to next parse method
            yield request
        else:
            self.logger.debug("mathematician: %s", asdict(mathematician))
            yield mathematician

        # follow urls for advisor and students
        self.logger.debug("following urls: %s", ", ".join(urls))
        yield from response.follow_all(urls, callback=self.parse)

    def parse_math_sci_net(self, response):
        mathematician = response.meta["mathematician"]
        trs = response.css("tr")
        self.logger.debug("trs: %s", trs)
        if trs:
            publication_trs = [tr for tr in trs if "total publications" in tr.get().lower()]
            self.logger.debug("publication_trs: %s", publication_trs)
            if publication_trs:
                publications = publication_trs[0].css("td:last-of-type::text").get()
                self.logger.debug("publications: %s", publications)
                mathematician.publications = int(publications) if publications else publications
            citation_trs = [tr for tr in trs if "total citations" in tr.get().lower()]
            self.logger.debug("citation_trs: %s", citation_trs)
            if citation_trs:
                citations = citation_trs[0].css("td:last-of-type::text").get()
                self.logger.debug("citations: %s", citations)
                mathematician.citations = int(citations) if citations else citations

        self.logger.debug("mathematician: %s", asdict(mathematician))

        yield mathematician

    def parse_a_selector(self, selector) -> Tuple[Optional[int], Optional[str]]:
        id_, url = None, None

        if not selector:
            return id_, url

        tag = selector.get()

        id_match = re.search(r"id=(\d+)", tag)
        if id_match:
            id_ = int(id_match.group(1))

        href_match = re.search(r'href="(.+)"', tag)
        if href_match:
            url = href_match.group(1)

        return id_, url
