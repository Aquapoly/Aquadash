FROM python:3.11-alpine

WORKDIR /usr/src/app

COPY devices/camera/client/ ./
COPY shared/ ./shared/

RUN ln -sfn /usr/src/app/shared /usr/src/shared

RUN pip install -r requirements.txt

RUN mkdir -p /timelapses && chown 1000:0 /timelapses && chmod 700 /timelapses

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000"]
