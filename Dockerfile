FROM python:3.10.0-alpine
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /server

COPY ./server/requirements.txt .

RUN \
 apk add --no-cache postgresql-libs && \
 apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev zlib-dev build-base jpeg-dev && \
 python3 -m pip install -r requirements.txt --no-cache-dir && \
 apk --purge del .build-deps

RUN apk add libjpeg-turbo

COPY ./server .

CMD [ "python", "manage.py" ]
EXPOSE 8000/tcp
LABEL org.opencontainers.image.description "MAAPS-Server"