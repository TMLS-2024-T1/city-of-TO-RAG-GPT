FROM python:3.12

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

COPY ./pull_data_requirements.txt .

RUN pip install --upgrade -r pull_data_requirements.txt

COPY ./scrapping_data.py .

ENTRYPOINT [ "python", "scrapping_data.py" ]

