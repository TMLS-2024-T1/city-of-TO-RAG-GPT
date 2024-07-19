#!/bin/bash

# download model
huggingface-cli login --token $HUGGINGFACE_TOKEN
huggingface-cli download meta-llama/Meta-Llama-3-8B-Instruct --local-dir ./model

# download data
python scrapping_data.py

