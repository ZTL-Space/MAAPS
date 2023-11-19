FROM python:3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /server

COPY ./server/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./server .

LABEL org.opencontainers.image.description "MAAPS-Server"