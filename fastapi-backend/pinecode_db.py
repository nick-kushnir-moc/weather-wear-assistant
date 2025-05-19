import numpy as np
import os
import json
from pinecone import Pinecone, Index, ServerlessSpec

api_key = 'dd5906ce-4275-4261-9698-897214864f12'  # Replace with your API key
pc = Pinecone(api_key=api_key)

# Define the index name and dimension
index_name = 'prompt-index'
dimension = 1536  # Adjust to your vector dimension

# Check if index exists and create if not
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=dimension,
        metric='cosine',
        spec=ServerlessSpec(
            cloud='aws',
            region='us-east-1'
        )
    )

# Use Index class to connect to the existing index
index = Index(api_key=api_key, name=index_name, cloud='aws', region='us-east-1', host='https://prompt-index-k59l4pa.svc.aped-4627-b74a.pinecone.io')

prompts_file = 'awesome-prompts/prompts.json'

if not os.path.isfile(prompts_file):
    print(f"Error: The file '{prompts_file}' does not exist.")
    exit(1)

if os.path.getsize(prompts_file) == 0:
    print(f"Error: The file '{prompts_file}' is empty.")
    exit(1)

try:
    with open(prompts_file, 'r') as file:
        prompts = json.load(file)
except json.JSONDecodeError as e:
    print(f"Error loading JSON file: {e}")
    exit(1)

# Prepare data for Pinecone
vectors = []
for prompt in prompts:
    prompt_vector = np.random.rand(dimension).tolist()  
    
    vectors.append({
        'id': prompt['id'],
        'values': prompt_vector,
        'metadata': prompt['metadata']
    })

# Upsert (insert or update) vectors to Pinecone index
index.upsert(vectors)
print(f"Uploaded {len(vectors)} prompts to Pinecone.")
