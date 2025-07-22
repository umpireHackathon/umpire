from google.cloud import storage
import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CR")

# Initialize the client
client = storage.Client()

# Define your bucket and file details
bucket_name = os.getenv("BUCKET_NAME")  # e.g., "my-bucket-name"
source_data = os.getenv("SAMPLE_JSON_DATA")  # e.g., "path/to/your/file.csv"
destination_file_name = "data/uploads/local_filename.csv"         # local path to save

# Get the bucket
bucket = client.bucket(bucket_name)
# Get the blob (file)
data = bucket.blob(source_data)

content = json.loads(data.download_as_text())

# ML MODELS
# Demand
def get_demand_model():
    """Fetches the demand model from the bucket."""
    BUCKET_NAME = os.getenv("BUCKET_NAME")
    DEMAND_FORECASTING_MODEL_PATH = os.getenv("DEMAND_FORECASTING_MODEL_PATH")
    TRAVEL_TIME_FORECASTING_MODEL_PATH = os.getenv("TRAVEL_TIME_FORECASTING_MODEL_PATH")
    demand_model_blob = bucket.blob(DEMAND_FORECASTING_MODEL_PATH)
    if demand_model_blob.exists():
        return demand_model_blob.download_as_bytes()
    else:
        raise FileNotFoundError("Demand model not found in the bucket.")

print(f"the data is {content}")
