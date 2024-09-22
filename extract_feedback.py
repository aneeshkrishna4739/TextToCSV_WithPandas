import csv
import json
from google.cloud import firestore

# Initialize Firestore client
db = firestore.Client()

# Function to extract feedback data from Firestore
def extract_feedback_data_from_firestore(collection_name='feedback'):
    feedback_data = []
    
    # Access the Firestore collection
    feedback_ref = db.collection(collection_name)
    
    # Get all documents in the collection
    docs = feedback_ref.stream()

    # Fetch each document's data
    for doc in docs:
        doc_data = doc.to_dict()
        prompt = doc_data.get('prompt', '')
        generated_code = doc_data.get('generated_code', '')
        feedback = doc_data.get('feedback', 0)  # assuming feedback is 0 or 1
        feedback_data.append((prompt, generated_code, feedback))
    
    return feedback_data

# Convert the feedback data to CSV format
def create_csv_for_finetuning(feedback_data, output_file='train.csv'):
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['text_input', 'output']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        
        for prompt, generated_code, feedback in feedback_data:
            generated_code = generated_code.replace("```python", "").replace("```", "")
            if feedback == 1:
                # Correctly concatenate the prompt with context
                full_prompt = prompt
                writer.writerow({
                    'text_input': full_prompt,
                    'output': generated_code
                })

def csv_to_json(csv_file, json_file):
    # Open the CSV file for reading
    with open(csv_file, mode='r', newline='') as file:
        # Read CSV file into a list of dictionaries
        csv_reader = csv.DictReader(file)
        data = [row for row in csv_reader]
    
    # Write the data into a JSON file
    with open(json_file, 'w') as file:
        json.dump(data, file, indent=4)

# Extract data from the firestore
feedback_data = extract_feedback_data_from_firestore()

# Create CSV file for fine-tuning
create_csv_for_finetuning(feedback_data)

# Convert the feedback CSV data into JSON format
csv_to_json("train.csv", "train.json")