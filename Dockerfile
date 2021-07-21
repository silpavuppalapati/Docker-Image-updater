FROM python:2.7
MAINTAINER Pamarthich

# Creating Application Source Code Directory
RUN mkdir -p /usr/src/app

#Setting Home Directory for containers
WORKDIR /usr/src/app

#Installing python Dependencies
COPY requirements.txt   /usr/src/app
RUN pip install --no-cache-dir  -r requirements.txt

# Copying source code to container
COPY . /usr/src/app

# Running Python Application
CMD ["python", "-u", "monitor.py"]

