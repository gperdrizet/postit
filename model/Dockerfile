FROM nvidia/cuda:11.4.3-runtime-ubuntu20.04

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Update & install python & pip
RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y python3 python3-pip
RUN python3 -m pip install --upgrade pip

# Set the working directory and move the source code in
WORKDIR /model
COPY . /model

# Install dependencies
RUN pip install -r requirements.txt

# Install bitsandbytes
WORKDIR /model/bitsandbytes-0.42.0
RUN python3 setup.py install

# Clean up
RUN rm -r /model/bitsandbytes-0.42.0

# Set the working directory back
WORKDIR /model