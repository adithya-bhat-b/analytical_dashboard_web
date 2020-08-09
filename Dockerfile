# Dockerfile

FROM python:3.7-buster

LABEL maintainer="Adithya Bhat <adithya.bhat@gmail.com>"

ARG DB_ENV
ARG BASE_DIR=/usr/app/src

ENV ENV=$DB_ENV
RUN mkdir -p $BASE_DIR
WORKDIR $BASE_DIR
COPY . .

RUN python -m pip install -r requirements.txt
RUN python manage.py migrate

EXPOSE 8020

ENTRYPOINT [ "python" ]
CMD [ "manage.py", "runserver" ]
