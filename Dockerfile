FROM python:3

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY setup.py ./
COPY math_genealogy .
RUN pip install -e .

WORKDIR math_genealogy/backend/scrapers

CMD [ "scrapy", "crawl", "math_genealogy" ]