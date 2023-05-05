# FROM python:3.9
# ENV PYTHONUNBUFFERED 1
# RUN mkdir /ml_rest_api
# WORKDIR /ml_rest_api
# COPY requirements.txt /ml_rest_api/
# RUN pip install -r requirements.txt
# COPY . /ml_rest_api/
# base image
# FROM python:3.9

# # set work directory
# WORKDIR /usr/src/app

# # install dependencies
# RUN apt-get update && \
#     apt-get -y install netcat && \
#     apt-get clean

# # install requirements
# COPY /requirements.txt .
# RUN pip install -r requirements.txt

# # copy source code
# COPY ./src/ml_rest_api .

# # run migrations
# RUN python manage.py migrate

# # collect static files
# RUN python manage.py collectstatic --noinput

# EXPOSE 8000

# CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]

# base image
# FROM python:3.9

# # set work directory
# WORKDIR /usr/src/app

# # install dependencies
# RUN apt-get update && \
#     apt-get -y install netcat && \
#     apt-get clean

# # install requirements
# COPY requirements.txt .
# RUN pip install -r requirements.txt

# # copy source code
# COPY ./src/ml_rest_api .

# # copy manage.py file
# COPY ./src/manage.py .

# # run migrations
# RUN python manage.py migrate

# # collect static files
# RUN python manage.py collectstatic --noinput

# EXPOSE 8000

# CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]

# base image
# FROM python:3.9

# # set work directory
# WORKDIR /usr/src/app

# # install dependencies
# RUN apt-get update && \
#     apt-get -y install netcat && \
#     apt-get clean

# # install requirements
# COPY requirements.txt .
# RUN pip install -r requirements.txt

# # add src directory to PYTHONPATH
# ENV PYTHONPATH="${PYTHONPATH}:/usr/src/app/src"

# # copy source code
# COPY ./src/ml_rest_api .

# # copy manage.py file
# COPY ./src/manage.py .

# # run migrations
# RUN python manage.py migrate

# # collect static files
# RUN python manage.py collectstatic --noinput

# EXPOSE 8000

# CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]

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
