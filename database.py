import os
from dotenv import load_dotenv
from supabase import create_client, Client

# STEP 1: Load the environment variables
# Call the load_dotenv() function so Python reads your .env file.
load_dotenv()

# STEP 2: Retrieve the secrets
# Use os.environ.get("YOUR_VARIABLE_NAME") to get the URL and Key.
# Assign them to variables named 'url' and 'key'.
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')


# STEP 3: Create the connection
# Pass your 'url' and 'key' variables into the create_client() function.
# We save this connection into a variable named 'supabase'.
supabase: Client = create_client(url,key)

if __name__ == "__main__":
    # Let's try to fetch 3 airports from the table you made yesterday
    response = supabase.table("airports").select("airport_name").limit(3).execute()
    print("Database Connection Successful!")
    print(response.data)