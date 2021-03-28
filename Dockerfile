FROM python:3.7-buster

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r ./requirements.txt
COPY setup.py ./
COPY math_genealogy ./math_genealogy
COPY scripts/crawl.sh ./scripts
RUN pip install -e .

WORKDIR math_genealogy/backend/scrapers

CMD [ "./scripts/crawl.sh" ]