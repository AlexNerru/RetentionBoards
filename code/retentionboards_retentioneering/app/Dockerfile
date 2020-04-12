# pull official base image
FROM jupyter/scipy-notebook

# set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# set work directory
WORKDIR /usr/src/app

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

# copy entrypoint.sh
COPY ./entrypoint.sh /usr/src/app/entrypoint.sh

# copy project
COPY . /usr/src/app/

USER root
RUN adduser --disabled-password --gecos '' newuser
# set work directory
RUN chown newuser /usr/src/app/
USER newuser

# run entrypoint.sh
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
