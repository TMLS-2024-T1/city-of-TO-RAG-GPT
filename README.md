
# City of Toronto RAG GPT
Hybrid agentic RAG + fine-tuned LLM system for Grounded city of Toronto Data Retrieval in Natural Language.

# Usage
To start the service up, create the `.env` variable with the following contents

```
OPENAI_API_KEY= # Your api key here
```

Then just run

```
docker compose up
```

If changes to build scripts have been made, rebuild.

```
docker compose up --build
```

