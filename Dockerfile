FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app

RUN mkdir -p reports

ARG TEST_TYPE=regression
ENV TEST_TYPE=${TEST_TYPE}

CMD ["sh", "-c", "pytest -n auto -m $TEST_TYPE --html=reports/report.html --junitxml=reports/junit.xml | tee output/$(date +%Y-%m-%dT%H-%M-%S).log"]