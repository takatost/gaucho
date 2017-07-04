FROM python:2.7-alpine3.6

WORKDIR /app

RUN apk add --update bash && rm -rf /var/cache/apk/*

RUN   pip install requests
RUN   pip install baker
RUN   pip install websocket-client

COPY services.py /app/gaucho
RUN chmod +x /app/gaucho

CMD ["/app/gaucho"]
