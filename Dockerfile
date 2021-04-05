FROM python:3.7-buster

WORKDIR /app

COPY requirements.prod.txt ./
RUN pip install --no-cache-dir -r ./requirements.prod.txt
COPY setup.py ./
COPY math_genealogy ./math_genealogy
RUN pip install -e .

CMD ["uvicorn", "math_genealogy.backend.app:app", "--host", "0.0.0.0", "--port", "80"]