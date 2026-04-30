from fastapi import APIRouter
from database import supabase
from models import AirportResponse
from typing import List

# Create the router
router = APIRouter(prefix="/airports", tags=["Airports"])

# Define the GET endpoint. It promises to return a List of AirportResponse objects.
@router.get("/", response_model=List[AirportResponse])
def get_airports():
    # YOUR CODE HERE: Write the Supabase query to select all columns ("*") 
    # from the "airports" table and order them by "airport_name".
    # (Hint: it looks very similar to the test query you just wrote in database.py, 
    # but use .order("airport_name") instead of .limit() )
    
    response = supabase.table('airports').select('*').order('airport_name').execute()
    
    # Return the data portion of the Supabase response
    return response.data