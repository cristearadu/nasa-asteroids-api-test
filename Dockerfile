FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app

RUN mkdir -p reports

ARG TEST_TYPE=regression
ENV TEST_TYPE=${TEST_TYPE}

CMD ["/bin/bash", "-c", "pytest -n auto -m ${TEST_TYPE:-regression} \
  --html=reports/report.html \
  --junitxml=reports/junit.xml \
  | tee output/docker_console_output.log"]