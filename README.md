# Self-Hosting Semantic Scholar Data

This repository contains all the code and instructions you'll need to begin your journey on self-hosting data from the Semantic Scholar datasets API using free AWS services. This code is provided by the team at [Moara.io](https://moara.io) as a thank you to Semantic Scholar and Ai2 for their efforts in propelling the world forward. Enjoy building!


## Prerequisites

#### Before starting, ensure you have the following:

- **Python 3.8 or higher**
- **Semantic Scholar API Key** (You can request it from [Semantic Scholar](https://www.semanticscholar.org/product/api#api-key-form))
- **An AWS Account**


## Project Structure

```plaintext
SS-self-hosting/
│
├── src/                        # Folder for source code
│   ├── download_datasets.py     # Script to download and upload datasets into AWS S3.
│   ├── query_datasets.py        # Script to query saved data using AWS Athena
│
├── config/                     # Configuration files
│   └── .env.template            # Template for environment variables
│
├── requirements.txt             # Python package dependencies at the project root
├── README.md                    # Comprehensive setup and usage instructions
├── LICENSE                      # License for the repository
```


## Setup


### 1. Clone the Repository
Start by cloning the repository to your local machine:
```bash
git clone https://github.com/sethmwatson-personal/SS-self-hosting.git
cd SS-self-hosting
```
### 2. Set Up a Python Virtual Environment
To ensure a clean workspace and avoid conflicts between dependencies, create and activate a virtual environment:


#### Step 1. Create the virtual environment:

```bash
python -m venv venv
```
#### Step 2. Activate the virtual environment:

#### On macOS/Unix/Linux:

```bash
source venv/bin/activate
```

#### On Windows:
```bash
venv\Scripts\activate
```
Once activated, your terminal prompt will be prefixed with (venv) to indicate that you're working within the virtual environment.


### 3. Install Dependencies
With the virtual environment activated, install the required Python packages by running:

```bash
pip install -r requirements.txt
```

This will install `boto3`, `pandas`, `requests`, and `python-dotenv`, which are needed for working with AWS services, handling data, and downloading datasets. It will also install `tqdm` which is a helpful import to visualize our progress.


### 4. Creating an IAM User with Correct Permissions

Once your AWS account is created, follow these steps to create an IAM user with the necessary permissions:

#### Step 1: Access the IAM Console

1. Log in to the [AWS Management Console](https://aws.amazon.com/console/).
2. In the search bar, type `IAM` and select the **IAM** service.

#### Step 2: Create a New IAM User

1. On the left sidebar, select **Users** and click **Create User**.
2. Enter a **User Name** (e.g., `your-name`).
3. Click **Next**.

#### Step 3: Attach Permissions

1. On the **Set permissions** page, choose **Attach policies directly** option.
2. In the search box, search for `AmazonS3FullAccess`.
3. Select the checkbox next to **AmazonS3FullAccess**.
4. Search for `AmazonDynamoDBFullAccess` and select the checkbox for that policy.
5. Click **Next**.

#### Step 4: Review and Create User

1. Review the details of the user and make sure the correct policies are attached: `AmazonS3FullAccess` and `AmazonDynamoDBFullAccess`.
2. Click **Create User**.

#### Step 5: Add programatic access to the user
1. Once the user is created, open the user details by clicking the user's name.
2. In the summary pane, select **Create access key**.
3. From the use case menu, select **Local code**.
4. Select the confirmation and click **Next**.
5. Enter a brief description and click **Create access key**.
6. You will see the **Access Key ID** and **Secret Access Key**. Download these credentials as a `.csv` file or copy them to a secure location. You will use these credentials to configure your AWS access in the `.env` file for this project.

### 5. Set Up AWS and Semantic Scholar API Credentials
After creating the AWS IAM user and retreiving your Semantic Scholar API key, you can now configure your .env file.

#### Step 1: Copy the environment template to create your .env file:

```bash
cp config/.env.template .env
```

#### Step 2: Edit the .env file to add your credentials and environment variables:
```plaintext
AWS_REGION=your-aws-region
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
S3_BUCKET_NAME=your-s3-bucket-name
ATHENA_DATABASE=your-athena-database
ATHENA_OUTPUT_BUCKET=s3://your-athena-output-s3-bucket/
SEMANTIC_SCHOLAR_API_KEY=your-api-key
```

Make sure to replace your-access-key-id, your-secret-access-key, and other placeholders with the appropriate values.


## Downloading and Uploading Data to S3

Once the setup is complete, you can download datasets from Semantic Scholar and upload them to your S3 bucket.

### Option A: Programmatic Setup (Recommended)
The script `download_datasets.py` will automatically check if the bucket exists. If the bucket does not exist, the script will create it for you. This ensures the process is streamlined and ready for downloading the datasets.

Run the following script:

```bash
python src/download_datasets.py
```
This script will:

1. Check if the S3 bucket exists; if not, it will create the bucket and name it based on your .env file.
2. Download/Stream the papers and abstracts datasets from Semantic Scholar.
3. Upload these datasets to the specified S3 bucket.

### Option B: Manual Setup via AWS Management Console
If you prefer to manually create the S3 bucket, follow these steps:

1. Log in to the AWS Management Console.
2. Navigate to S3.
3. Click Create bucket.
4. Name your bucket (e.g., my-semanticscholar-bucket), select a region, and click Create.

#### Important: Once your S3 bucket is ready, ensure the S3_BUCKET_NAME in your .env file matches the name of the bucket you've manually created. After creating the bucket, you must still run the following script to download and upload the datasets to your S3 bucket:

```bash
python src/download_datasets.py
```


## Querying the Data