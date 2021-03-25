import random
import re
import json
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


class MathGenealogySpider(scrapy.Spider):
    name = "math_genealogy"
    download_delay = 0.25

    # start_urls = [
    #     f'https://www.mathgenealogy.org/id.php?id={i}'
    #     for i in random.sample(range(1, 265263 + 1), k=1000)
    # ]

    start_urls = [
        'https://www.mathgenealogy.org/id.php?id=62'
    ]

    def parse(self, response):
        print('accessed page %s', response.url)

        # instantiate data class
        mathematician = Mathematician()

        mathematician.math_genealogy_url = str(response.url)

        # get id
        id_match = re.search(r'id=(\d+)', response.url)
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
            graduated_match = re.search('\D(\d{4})\D', graduated_span)
            if graduated_match:
                mathematician.graduated = int(graduated_match.group(1))

        # get thesis title
        mathematician.thesis = response.css('#thesisTitle::text').get()

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
        mathematician_a_selectors = [s for s in mathematician_a_selectors if "Chrono=" not in s.get()]
        # student links are inside a table, but advisor links are outside the table
        student_selectors = response.css('table a[href^="id.php?id="]')
        student_text = set(map(lambda x: x.get(), student_selectors))

        advisor_selectors = [
            s for s in mathematician_a_selectors
            if s.get() not in student_text]

        for advisor_selector in advisor_selectors:
            advisor_id, advisor_url = self.parse_a_selector(advisor_selector)
            mathematician.advisor_ids.append(advisor_id)
            urls.append(advisor_url)

        for student_selector in student_selectors:
            student_id, student_url = self.parse_a_selector(student_selector)
            mathematician.student_ids.append(student_id)
            urls.append(student_url)

        # get subject
        mathematician.subject = response.css('div[style="text-align: center; margin-top: 1ex"]::text').get()

        # get link to MathSciNet if it exists
        math_sci_net_a_tag = response.css('a[href^="http://www.ams.org/mathscinet/MRAuthorID"]').get()
        if math_sci_net_a_tag:
            math_sci_net_url_match = re.search('href="(.+)"', math_sci_net_a_tag)
            if math_sci_net_url_match:
                mathematician.math_sci_net_url = math_sci_net_url_match.group(1)

        # write to a file
        with open(f'data/math_genealogy/mathematician-{mathematician.id_}', 'w') as f:
            f.write(json.dumps(asdict(mathematician), indent=2, default=str))

        # follow urls for advisor and students

    def parse_a_selector(self, selector) -> Tuple[Optional[int], Optional[str]]:
        id_, url = None, None

        if not selector:
            return id_, url

        tag = selector.get()

        id_match = re.search('id=(\d+)', tag)
        if id_match:
            id_ = int(id_match.group(1))

        href_match = re.search('href="(.+)"', tag)
        if href_match:
            url = href_match.group(1)

        return id_, url
