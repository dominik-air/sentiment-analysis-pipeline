FROM python:3.10

WORKDIR /app

COPY ./api/requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt

COPY ./api /app

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
