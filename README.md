# Self-Hosting Semantic Scholar Data

This repository contains all the code and instructions you'll need to begin your journey on self-hosting data from the Semantic Scholar datasets API using free AWS services. This code is provided by the team at [Moara.io](https://moara.io) as a thank you to Semantic Scholar and Ai2 for their efforts in propelling the world forward. Enjoy building!

These instructions will walk you through:                                                                                                                                                   
Downloading the Semantic Scholar datasets → Creating searchable tables → Querying the data → Optionally join datasets to create more meaningful views of the datasets.


## Prerequisites

#### Before starting, ensure you have the following:

- **Python 3.8 or higher**
- **Semantic Scholar API Key** (You can request it from [Semantic Scholar](https://www.semanticscholar.org/product/api#api-key-form))
- **An AWS Account**
- **Basic understanding of Python and SQL**


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
├── samplelines.json             # Example lines from all 10 datasets.
```


## Setup


### 1. Clone the Repository
Start by cloning the repository to your local machine:
```bash
git clone https://github.com/moaraio/SS-self-hosting.git
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
4. Search for `AmazonAthenaFullAccess` and select the checkbox for that policy.
5. Click **Next**.

#### Step 4: Review and Create User

1. Review the details of the user and make sure the correct policies are attached: `AmazonS3FullAccess` and `AmazonAthenaFullAccess`.
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

#### Step 2: Edit the .env file to add your credentials and variables:
```plaintext
AWS_REGION=your-aws-region
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
S3_BUCKET_NAME=your-s3-bucket-name
ATHENA_OUTPUT_BUCKET=s3://<your-s3-bucket-name>/query-results/
SEMANTIC_SCHOLAR_API_KEY=your-api-key
```

Make sure to replace your-access-key-id, your-secret-access-key, and other placeholders with the appropriate values. Note you will use your s3 bucket name twice.


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

#### Important: Once your S3 bucket is ready, ensure the S3_BUCKET_NAME and ATHENA_OUTPUT_BUCKET in your .env file matches the name of the bucket you've manually created. After creating the bucket, you must still run the following script to download and upload the datasets to your S3 bucket:

```bash
python src/download_datasets.py
```


## Querying the Data
Once you have uploaded your datasets to S3, the next step is to query this data using AWS Athena.

#### Before creating tables, consider what data you’ll be querying. Each dataset has multiple fields, but you may only need a subset of them depending on your use case. For example, if you’re only interested in papers titles, years, and authors, you can create a table with just these fields from the papers dataset. For a full list of available fields across the datasets, see this document (ADD DOCUMENT LINK). Use it to understand what data you need before proceeding with table creation and querying.

### 1. Setting up Athena Database and Table(s)
You can set up your Athena database and tables either through the Athena UI or programmatically using the provided scripts. Below is an overview of both methods.

#### Step 1. Create a Database
First, you need to create a database in Athena. If you're using the query_datasets.py file, the default database is set to webinar, but you can modify this to fit your needs. Run the following query in the Athena UI or programmatically to create the database:

```sql
CREATE DATABASE IF NOT EXISTS webinar;
```
This creates a database called webinar. If you'd like to name it something else, replace webinar with your preferred database name.

#### Step 2. Create a Table
Once the database is created, you can proceed with creating a table. Here’s an example of how to create a table named 'papers' within the 'webinar' database, which will reference the papers dataset you uploaded to S3:

```sql
CREATE EXTERNAL TABLE IF NOT EXISTS webinar.papers (
    corpusid INT,
    url STRING,
    title STRING,
    authors ARRAY<STRUCT<authorId:STRING, name:STRING>>,
    year INT,
    s2fieldsofstudy ARRAY<STRUCT<category:STRING source:STRING>>,
    journal STRUCT<name:STRING, volume:STRING, pages:STRING>
)
ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe'
WITH SERDEPROPERTIES (
  'ignore.malformed.json' = 'true'
)
LOCATION 's3://<your-s3-bucket-name>/<your-object-folder>/'
TBLPROPERTIES ('has_encrypted_data'='false');
```
In this query:

- You can modify the database and table names.
- You can modify the fields in this query to suit your data needs.
- Replace `LOCATION 's3://<your-s3-bucket-name>/<your-object-folder>/'` with the name of your S3 bucket and object folder path you created above.

Alternatively, you can run the above queries programmatically using Python. The `query_datasets.py` script will allow you to run queries via AWS Athena by using the custom_query() function which will be described below.

### 2. Running Queries Using `query_datasets.py`
Once your tables are set up, you can query your data using either the Athena UI or the provided query_datasets.py script. This script is pre-configured for common queries, but it also allows you to modify and extend it to suit your needs.

#### Configuration
At the top of the query_datasets.py script, you'll find a few key configuration settings:

```python
DATABASE = 'webinar'
TABLE = 'papers'
OUTPUT_LOCATION = os.getenv('ATHENA_OUTPUT_BUCKET')
```

- DATABASE: Ensure this matches the name of the database you created (e.g., webinar).
- TABLE: Replace with the table name you want to query (e.g., papers).
- OUTPUT_LOCATION: This should correspond to the ATHENA_OUTPUT_BUCKET value in your .env file.

#### Running the Script

To start querying, run the following command from your terminal:

```bash
python src/query_datasets.py
```
You’ll be prompted to choose from several query options:

- Find papers by field of study: Enter the field (e.g., "Medicine" or "Economics").
- Find papers by author: Enter part or all of an author’s name (partial matches are supported).
- Find papers by journal: Enter the journal name.
- Run a custom query: Enter your own SQL query for Athena. 


#### Example Query: 

Find Papers by Field of Study
Selecting option 1 to find papers by field of study will run a query like the following:

```sql
SELECT p.title, p.authors, p.journal.name, p.year
FROM webinar.papers p, UNNEST(p.s2fieldsofstudy) AS t (field)
WHERE field.category = 'Medicine'
LIMIT 5;
```
The results will be displayed in the terminal, listing the paper titles, authors, journal names, and years.

#### Custom Queries
You can input custom queries by selecting option "4". Here’s an example for counting the total number of papers:

```sql
SELECT COUNT(*) FROM webinar.papers;
```

### 3. Creating and Editing Queries

You are not limited to the predefined query options in `query_datasets.py` file. You can create your own query functions by adding new queries directly into the script. For instance, you could add more filters, join dataset tables together, or even aggregate functions to create complex queries that match your specific use cases.

**TIP: The queries provided in the script have a 'LIMIT' defined to return only a subset of results for efficiency, and the author query uses the 'LIKE' clause to allow partial matches. Get creative and build your own queries by experimenting with different SQL clauses.**

Feel free to modify the script, create as many custom queries as you want, and extend it to suit your needs. Alternatively, you can create and save custom queries using the Athena UI for a more visual approach.

## Semantic Scholar API official documentation and additional resources

If you have concerns or feedback specific to this library, feel free to [open an issue](https://github.com/moaraio/SS-self-hosting/issues). However, the official documentation provides additional resources for broader API-related issues.

- For details on Semantic Scholar APIs capabilities and limits, [go to the official documentation](https://api.semanticscholar.org/api-docs/datasets).
- The [Frequently Asked Questions](https://www.semanticscholar.org/faq) page also provides helpful content if you need a better understanding of data fetched from Semantic Scholar services.
- This [official GitHub repository](https://github.com/allenai/s2-folks) allows users to report issues and suggest improvements.
- There is also a community on [Slack](https://join.slack.com/t/semanticschol-xyj3882/shared_invite/zt-2e98pwubp-vzoxaTgITyurw~~WK1OntQ). Highly recommend!
