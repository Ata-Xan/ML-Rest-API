# base image
FROM python:3.9

# set work directory
WORKDIR /usr/src/app

# install dependencies
RUN apt-get update && \
    apt-get -y install netcat && \
    apt-get clean

# install requirements
COPY requirements.txt /usr/src/app/requirements.txt
RUN pip install -r /usr/src/app/requirements.txt

# add src directory to PYTHONPATH
ENV PYTHONPATH="${PYTHONPATH}:/usr/src/app/src"

# copy source code
COPY ./src/ml_rest_api /usr/src/app/src/ml_rest_api

# copy manage.py file
COPY ./src/manage.py /usr/src/app/src/manage.py

# run migrations
RUN python /usr/src/app/src/manage.py migrate

# collect static files
RUN python /usr/src/app/src/manage.py collectstatic --noinput

EXPOSE 8000

CMD [ "python", "/usr/src/app/src/manage.py", "runserver", "0.0.0.0:8000" ]
