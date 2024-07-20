from flask import Flask, request, jsonify
from transformers import pipeline
import torch
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
model_path = os.path.abspath(dir_path + '/model/')

pipeline = pipeline(
    "text-generation",
    model=model_path,
    model_kwargs={"torch_dtype": torch.bfloat16},
    device="cuda",
)

app = Flask(__name__)

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    prompt = data.get('prompt', '')
    response = pipeline(
        f"""
            Don't return the prompt. The following is the prompt:
            {prompt}
        """,
        max_new_tokens=150
    )
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888)

