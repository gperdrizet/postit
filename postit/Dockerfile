FROM python:3.10-slim-bookworm

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Update & install python 3.8 & pip
RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y python3 python3-pip
RUN python3 -m pip install --upgrade pip

# Set the working directory and move the source code in
WORKDIR /postit
COPY . /postit

# Install dependencies
RUN pip install -r requirements.txt