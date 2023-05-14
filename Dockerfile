# base image
FROM python:3.9

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# set work directory
WORKDIR /usr/src/ml-rest-api

# add label
LABEL Name=my-app

# install dependencies
RUN apt-get update && \
    apt-get -y install netcat && \
    apt-get -y install netcat postgresql-client &&\
    apt-get clean


# install requirements
RUN pip install --upgrade pip
RUN pip install django-filter
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# add src directory to PYTHONPATH
# ENV PYTHONPATH="${PYTHONPATH}:/usr/src/ml-rest-api/src"

# copy source code
COPY . .
