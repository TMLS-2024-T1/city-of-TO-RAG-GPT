FROM langchain/langchain

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

COPY demo_requirements.txt .

RUN pip install --upgrade -r demo_requirements.txt

COPY demo.py .
COPY eval.py .

ENTRYPOINT [ "python", "demo.py" ]

