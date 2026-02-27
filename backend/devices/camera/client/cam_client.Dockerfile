FROM python:3.11-alpine

WORKDIR /usr/src/app

COPY . .

RUN pip install -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000"]
