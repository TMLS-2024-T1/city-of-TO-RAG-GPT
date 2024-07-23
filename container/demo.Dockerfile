FROM langchain/langchain

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.in .
COPY requirements.txt .

RUN pip install --upgrade -r requirements.txt

COPY demo.py .
COPY chain.py .

ENTRYPOINT [ "python", "demo.py" ]

