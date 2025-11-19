FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --timeout 60 --retries 10 -r requirements.txt

COPY api.py .
COPY stats.py .
COPY cache.py .
COPY ml/ ./ml/
COPY index.html .
COPY data/ ./data/

EXPOSE 8000

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
