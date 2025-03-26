FROM python:3.11-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN apk update && apk add \
    libpq \
    postgresql-dev \
    build-base \
    linux-headers

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

RUN apk del \
    linux-headers

COPY . .

CMD [ "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000" ]