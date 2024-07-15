import pandas as pd
import openai
from openai import OpenAI
import os
import re

# Initialize OpenAI with your API key
os.environ['OPENAI_API_KEY'] = #redacted key
openai.api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def sanitize_dataframe_name(name):
    # Replace invalid characters with underscores and ensure it doesn't start with a number
    sanitized_name = re.sub(r'\W|^(?=\d)', '_', name)
    return sanitized_name

def load_csv_files(file_paths):
    dataframes = {}
    for file_path in file_paths:
        df_name = sanitize_dataframe_name(file_path.split('/')[-1].split('.')[0])
        dataframes[df_name] = pd.read_csv(file_path)
    return dataframes

def generate_context(dataframes):
    context = ""
    for name, df in dataframes.items():
        context += f"Data frame name to consider for df name is: {name}. Make sure your name make sense.\nSample Column names and rows:\n{df.head().to_csv(index=False)}\n\n"
    return context

def generate_pandas_query(question, context):
    prompt = f"""
    Given the following DataFrame information:
    {context}

    Answer the following question with a specific pandas query. Ensure the query references the correct DataFrame by name:
    {question}

    Makesure to use the corresponding name from the data frame name instead of just df.
    """
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150
    )
    response_text = response.choices[0].message.content.strip()
    
    # Extract the actual query from the response
    query_start = response_text.find("```")
    query_end = response_text.rfind("```")
    
    if query_start != -1 and query_end != -1:
        query = response_text[query_start+10:query_end].strip()
    else:
        lines = response_text.split('\n')
        query_lines = [line for line in lines if 'import pandas as pd' not in line and '```' not in line and 'You can find' not in line]
        query = '\n'.join(query_lines).strip()
    print(query)
    return query

def execute_pandas_query(dataframes, query):
    locals().update(dataframes)
    # Use exec to execute multi-line code
    exec(query)

def main(file_paths, question):
    # Step 1: Retrieve relevant CSVs
    #relevant_csvs = retrieve_relevant_csvs(question, file_paths)
    relevant_csvs = file_paths
    # Step 2: Load CSV files
    dataframes = load_csv_files(relevant_csvs)
    
    # Step 3: Generate context from CSV files
    context = generate_context(dataframes)
    
    # Step 4: Generate pandas query using OpenAI's GPT model
    pandas_query = generate_pandas_query(question, context)
    print(f"Generated Pandas Query:\n{pandas_query}\n")
    
    # Step 5: Execute the pandas query
    execute_pandas_query(dataframes, pandas_query)
    
    # Extract and return the result
    result = locals().get('result', None)
    return result

# Example usage
file_paths = ['/teamspace/studios/this_studio/data/datasets/2024-city-budget-pre-budget-consultation/resources/2024 Pre-Budget Consultation exchange data Open Data CSV.csv']  # Replace with your actual file paths
question = "What is the top 10 average rating entry row number"

result = main(file_paths, question)
print("Query Result:")
print(result)
