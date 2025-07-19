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


print(f"the data is {content}")
