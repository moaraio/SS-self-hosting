import requests
import boto3
import os
from tqdm import tqdm
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# AWS S3 setup
aws_region = os.getenv('AWS_REGION')  
s3_client = boto3.client('s3', region_name=aws_region)
bucket_name = os.getenv('S3_BUCKET_NAME')

# Validate S3 bucket name
if not bucket_name:
    raise ValueError("S3 bucket name is not set. Please check your .env file.")

# Helper function to stream the file directly to S3 with a progress bar
def stream_file_to_s3(url, bucket_name, object_name):
    response = requests.get(url, stream=True)
    response.raise_for_status()  # Check if the request was successful

    # Get the total file size in bytes
    total_size = int(response.headers.get('content-length', 0))

    # Progress bar for both downloading and uploading
    with tqdm(total=total_size, unit='iB', unit_scale=True, desc=f"Processing {object_name}", ncols=100) as progress:
        s3_client.upload_fileobj(response.raw, bucket_name, object_name, Callback=lambda bytes_transferred: progress.update(bytes_transferred))

# Function to download all files for a dataset and upload to S3
def download_dataset_to_s3(dataset_name, dataset_urls):
    print(f"Retrieved {len(dataset_urls)} files from {dataset_name} dataset...")
    
    for counter, url in enumerate(dataset_urls, start=1):
        object_name = f"{dataset_name}/file{counter}.json.gz"
        print(f"\nProcessing {object_name} to s3://{bucket_name}/{object_name}")
        
        try:
            stream_file_to_s3(url, bucket_name, object_name)
            print(f"Successfully processed {object_name}")
        except Exception as e:
            print(f"\nError processing {object_name}: {e}")

# Main function to fetch dataset metadata and download files
def main():
    try:
        api_key = os.getenv('SEMANTIC_SCHOLAR_API_KEY')
        if not api_key:
            raise ValueError("Semantic Scholar API key is not set. Please check your .env file.")
        
        headers = {
            'x-api-key': api_key
        }

        dataset_urls = {
            "papers": "https://api.semanticscholar.org/datasets/v1/release/latest/dataset/papers",
            "abstracts": "https://api.semanticscholar.org/datasets/v1/release/latest/dataset/abstracts"
        }

        # Fetch dataset metadata and download files
        for dataset_name, dataset_url in dataset_urls.items():
            print(f"\nFetching metadata for {dataset_name} dataset...")
            response = requests.get(dataset_url, headers=headers)
            response.raise_for_status()
            dataset_metadata = response.json()
            
            file_urls = dataset_metadata.get('files', [])
            if file_urls:
                download_dataset_to_s3(dataset_name, file_urls)
            else:
                print(f"No files found for {dataset_name}")
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching dataset metadata: {e}")

if __name__ == "__main__":
    main()
