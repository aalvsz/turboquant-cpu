FROM python:3.7

RUN mkdir -p /workspace/turboquant
WORKDIR /workspace/turboquant
COPY . /workspace/turboquant

RUN apt-get update && apt-get install -y jq
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements-dev.txt
