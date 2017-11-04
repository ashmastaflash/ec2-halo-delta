FROM alpine:3.4
MAINTAINER ashmastaflash

RUN apk add -U \
    python=2.7.12-r0 \
    py-pip=8.1.2-r0

RUN mkdir /app

COPY app/ /app/

RUN pip install -r /app/requirements.txt

CMD ["/usr/bin/python", "/app/application.py"]
