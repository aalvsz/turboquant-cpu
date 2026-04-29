# This file is a template, and might need editing before it works on your project.
FROM python:3.7

RUN mkdir /opt/project
WORKDIR /opt/project
COPY . /opt/project

RUN apt-get update && apt-get install -y jq
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements-dev.txt

# For some other commands
# CMD ["python", "app.py"]
