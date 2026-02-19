FROM python:3.11-alpine

WORKDIR /usr/src/app

RUN apk update && apk add \
    libpq \
    postgresql-dev \
    build-base \
    linux-headers \
    ffmpeg

COPY requirements.txt ./

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

RUN apk del \
    linux-headers

COPY . .

CMD [ "uvicorn", "src.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000" ]