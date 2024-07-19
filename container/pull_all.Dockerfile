FROM python:3.12

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements.in .
COPY ./requirements.txt .

RUN pip install --upgrade -r requirements.txt

COPY ./pull-all.sh .
COPY ./scrapping_data.py .

ARG HUGGINGFACE_TOKEN
ENV HUGGINGFACE_TOKEN=${HUGGINGFACE_TOKEN}

ENTRYPOINT [ "bash", "-c", "/app/pull-all.sh" ]

