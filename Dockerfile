FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p workspace

EXPOSE 8000

CMD ["uvicorn", "app.api.report_generator:app", "--host", "0.0.0.0", "--port", "8000"]

# Comando alternativo per il generatore diretto
# Per usarlo: docker run -p 8000:8000 --env OPENAI_API_KEY=<chiave> -e CMD_ALTERNATIVE=true <immagine>
ENV CMD_ALTERNATIVE=false
RUN chmod +x report_generator_direct.py
CMD /bin/bash -c 'if [ "$CMD_ALTERNATIVE" = "true" ]; then python -m report_generator_direct; else uvicorn app.api.report_generator:app --host 0.0.0.0 --port 8000; fi'
