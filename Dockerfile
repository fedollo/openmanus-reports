FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p workspace

EXPOSE 8001

CMD ["uvicorn", "app.api.report_generator:app", "--host", "0.0.0.0", "--port", "8001"]
