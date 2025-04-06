FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app

RUN mkdir -p reports

CMD ["pytest", "-n", "auto", "-m", "regression", "--html=reports/report.html", "--junitxml=reports/junit.xml"]
