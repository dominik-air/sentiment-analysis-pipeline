FROM --platform=amd64 python:3.10-slim

WORKDIR /api

COPY . /api/

RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]