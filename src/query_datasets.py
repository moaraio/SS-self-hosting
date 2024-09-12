import boto3
import time
import os
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Athena client
athena_client = boto3.client('athena', region_name=os.getenv('AWS_REGION'))

# Configuration - Defined directly in the script for simplicity
DATABASE = 'webinar'  # Replace with your database name
TABLE = 'papers'  # Replace with the table name you want to query
OUTPUT_LOCATION = os.getenv('ATHENA_OUTPUT_BUCKET')  # Keep this in the .env as it should not change frequently.

# Run an Athena query.
def execute_athena_query(query):
    response = athena_client.start_query_execution(
        QueryString=query,
        QueryExecutionContext={'Database': DATABASE},
        ResultConfiguration={'OutputLocation': OUTPUT_LOCATION}
    )
    query_execution_id = response['QueryExecutionId']
    return query_execution_id

# Wait for query completion
def wait_for_query_to_complete(query_execution_id):
    while True:
        response = athena_client.get_query_execution(QueryExecutionId=query_execution_id)
        status = response['QueryExecution']['Status']['State']
        if status == 'SUCCEEDED':
            print("Query succeeded.")
            break
        elif status == 'FAILED':
            raise Exception("Query failed.")
        elif status == 'CANCELLED':
            raise Exception("Query was cancelled.")
        else:
            print(f"Query is in state: {status}, waiting...")
            time.sleep(5)  # Wait for 5 seconds before checking again

# Get the results from the Athena query
def get_query_results(query_execution_id):
    result = athena_client.get_query_results(QueryExecutionId=query_execution_id)
    rows = result['ResultSet']['Rows']
    columns = [col['VarCharValue'] for col in rows[0]['Data']]
    data = [[col.get('VarCharValue', '') for col in row['Data']] for row in rows[1:]]
    df = pd.DataFrame(data, columns=columns)
    return df

# Query to find papers by field of study. 
def query_papers_by_field_of_study(field_of_study):
    query = f'''
        SELECT p.title, p.authors, p.journal.name, p.year
        FROM {DATABASE}.{TABLE} p, UNNEST(p.s2fieldsofstudy) AS t (field)
        WHERE field.category = '{field_of_study}'
        LIMIT 5;
    '''
    query_id = execute_athena_query(query)
    wait_for_query_to_complete(query_id)  # Wait for the query to complete
    df = get_query_results(query_id)
    # Rename columns for clarity
    df.columns = ['Title', 'Authors', 'Journal', 'Year']
    return df

# Query to find papers by author. This uses the 'LIKE' to allow partial matches
def query_papers_by_author(author_name):
    query = f'''
        SELECT p.title, p.authors, p.journal.name, p.year
        FROM {DATABASE}.{TABLE} p, UNNEST(p.authors) AS t (author)
        WHERE author.name LIKE '%{author_name}%'
        LIMIT 5;
    '''
    query_id = execute_athena_query(query)
    wait_for_query_to_complete(query_id)  # Wait for the query to complete
    df = get_query_results(query_id)
    df.columns = ['Title', 'Authors', 'Journal', 'Year']
    return df

# Query to find papers by journal.
def query_papers_by_journal(journal_name):
    query = f'''
        SELECT p.title, p.authors, p.journal.name, p.year
        FROM {DATABASE}.{TABLE} p
        WHERE p.journal.name = '{journal_name}'
        LIMIT 5;
    '''
    query_id = execute_athena_query(query)
    wait_for_query_to_complete(query_id)  # Wait for the query to complete
    df = get_query_results(query_id)
    df.columns = ['Title', 'Authors', 'Journal', 'Year']
    return df

# Custom Athena query.
def custom_query():
    query = input("Enter your custom SQL query: ")
    
    if not query.strip():  # Prevent running empty queries
        print("Error: SQL query cannot be empty. Please enter a valid query.")
        return pd.DataFrame()  # Return empty DataFrame if no query

    try:
        query_id = execute_athena_query(query)
        wait_for_query_to_complete(query_id)  # Wait for the query to complete
        df = get_query_results(query_id)
        
        if df.empty:
            print("No results found for the query.")
        return df

    except Exception as e:
        print(f"Error executing the custom query: {e}")
        return pd.DataFrame()  # Return empty DataFrame if there's an error

# Main function with query options
def main():
    print("Choose a query to run:")
    print("1. Find papers by field of study")
    print("2. Find papers by author")
    print("3. Find papers by journal")
    print("4. Run a custom query")
    
    choice = input("Enter the number of the query you want to run: ")
    
    if choice == "1":
        field_of_study = input("Enter the field of study: ")
        df = query_papers_by_field_of_study(field_of_study)
        print(df if not df.empty else "No papers found for this field of study.")
    elif choice == "2":
        author_name = input("Enter the author's name: ")
        df = query_papers_by_author(author_name)
        print(df if not df.empty else f"No papers found for author: {author_name}.")
    elif choice == "3":
        journal_name = input("Enter the journal name: ")
        df = query_papers_by_journal(journal_name)
        print(df if not df.empty else f"No papers found for journal: {journal_name}.")
    elif choice == "4":
        df = custom_query()
        if not df.empty:
            print(df)
    else:
        print("Invalid choice. Please select a valid option.")

if __name__ == "__main__":
    main()
