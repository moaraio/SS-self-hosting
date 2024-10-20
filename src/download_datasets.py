import requests
import boto3
import os
from tqdm import tqdm
from dotenv import load_dotenv
from botocore.exceptions import ClientError

# Load environment variables
load_dotenv()

# AWS S3 setup
aws_region = os.getenv('AWS_REGION')
s3_client = boto3.client('s3', region_name=aws_region)
bucket_name = os.getenv('S3_BUCKET_NAME')

# Validate S3 bucket name
if not bucket_name:
    raise ValueError("S3 bucket name is not set. Please check your .env file.")

# Helper function to check if a bucket exists, and if not, create it
def check_and_create_bucket(bucket_name, aws_region):
    try:
        # Check if the bucket exists
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"Bucket {bucket_name} already exists.")
    except ClientError as e:
        error_code = e.response['Error']['Code']
        # Bucket doesn't exist, so let's create it
        if error_code == '404':
            print(f"Bucket {bucket_name} does not exist. Creating it...")
            try:
                # Create bucket, handle region-specific case
                if aws_region == 'us-east-1':
                    s3_client.create_bucket(Bucket=bucket_name)
                else:
                    s3_client.create_bucket(
                        Bucket=bucket_name,
                        CreateBucketConfiguration={
                            'LocationConstraint': aws_region
                        }
                    )
                print(f"Bucket {bucket_name} created successfully.")
            except ClientError as create_error:
                print(f"Failed to create bucket {bucket_name}: {create_error}")
                raise
        else:
            # Handle other errors related to the bucket
            print(f"Error checking bucket: {e}")
            raise


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

        # Check and create the S3 bucket if it doesn't exist
        check_and_create_bucket(bucket_name, aws_region)

        # Here you can modify which datasets you'd like to download and upload to s3.
        dataset_urls = {
            "papers": "https://api.semanticscholar.org/datasets/v1/release/latest/dataset/papers",
            
            # You can add additional URLs below such as: 
            # "abstracts": "https://api.semanticscholar.org/datasets/v1/release/latest/dataset/abstracts",
            # "tldrs": "https://api.semanticscholar.org/datasets/v1/release/latest/dataset/tldrs",
            #"citations": "https://api.semanticscholar.org/datasets/v1/release/latest/dataset/citations"
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
