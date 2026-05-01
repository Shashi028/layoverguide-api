from fastapi import APIRouter, HTTPException, Depends
from typing import List
from database import supabase
from models import ItineraryResponse, ItineraryCreate
from uuid import UUID
from auth import verify_token

# 1. Create the router
router = APIRouter(prefix="/itineraries", tags=["Itineraries"])

# 2. Define the GET endpoint
@router.get("", response_model=List[ItineraryResponse])
def search_itineraries(airport_id: str, min_hrs: float, max_hrs: float):
    
    # Your database stores time in minutes, but users search in hours.
    min_mins = int(min_hrs * 60)
    max_mins = int(max_hrs * 60)

    response = supabase.table('itineraries').select('*').eq("airport_id", airport_id).gte("layover_duration_mins", min_mins).lte("layover_duration_mins", max_mins).execute()
    
    return response.data

@router.get("/{itinerary_id}")
async def get_itinerary(itinerary_id: UUID):
    try:
        result = supabase.table('itineraries').select('*, upvotes(count)').eq('itinerary_id', itinerary_id).single().execute()
        return result.data
    except:
        raise HTTPException(status_code=404, detail="Itinerary not found")
    
@router.post("", status_code=201)
async def create_itinerary(itinerary: ItineraryCreate, user_id: str = Depends(verify_token)):
    
    # Step 1: Check airport exists
    airport = supabase.table('airports').select('*').eq('airport_id', itinerary.airport_id).execute()
    if not airport.data:
        raise HTTPException(status_code=404, detail="Airport not found")
    
    # Step 2: Validate time_to_exit_mins
    if itinerary.time_to_exit_mins is not None:
        if itinerary.time_to_exit_mins > itinerary.layover_duration_mins:
            raise HTTPException(status_code=400, detail="Exit time cannot exceed layover duration")
    
    # Step 3: Build the data dict and insert
    data = itinerary.model_dump(mode='json')
    data['user_id'] = user_id 
    
    result = supabase.table('itineraries').insert(data).execute()
    return result.data[0] 

@router.post("/{itinerary_id}/upvote")
async def toggle_upvote(itinerary_id: UUID, user_id: str = Depends(verify_token)):
    
    # STEP 1: Check if the upvote already exists.
    # YOUR CODE HERE: Query the 'upvotes' table. 
    # Chain TWO .eq() filters: one for user_id, one for itinerary_id.
    existing_vote = supabase.table('upvotes').select('*').eq('user_id',user_id).eq('itinerary_id',str(itinerary_id)).execute()
    
    # Check if the query returned any data
    if len(existing_vote.data) > 0:
        # STEP 2: The upvote exists, so we want to DELETE it (un-upvote)
        # Hint: supabase.table('upvotes').delete().eq(...).eq(...).execute()
        supabase.table('upvotes').delete().eq('user_id',user_id).eq('itinerary_id',str(itinerary_id)).execute()
        return {"upvoted": False, "message": "Upvote removed"}
        
    else:
        # STEP 3: The upvote does not exist, so we want to INSERT it
        # Hint: You need to insert a dictionary with 'user_id' and 'itinerary_id'
        supabase.table('upvotes').insert({'user_id':user_id,'itinerary_id':str(itinerary_id)}).execute()
        
        return {"upvoted": True, "message": "Upvote added"}