from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

# This class defines what an Airport looks like when we send it to the user.
class AirportResponse(BaseModel):
    airport_id: UUID
    iata_code: str
    airport_name: str
    city: str
    country: str
    timezone: str
    
class ItineraryResponse(BaseModel):
    itinerary_id: UUID
    airport_id: UUID
    user_id: UUID
    layover_duration_mins: int
    time_to_exit_mins: Optional[int] = None
    arrival_terminal: Optional[str] = None
    departure_terminal: Optional[str] = None
    user_rating: Optional[int] = None
    notes: Optional[str] = None
    submission_date: datetime
    upvotes: list = []
    upvote_count: int = 0

class ItineraryCreate(BaseModel):
    airport_id: UUID
    layover_duration_mins: int = Field(..., gt=0)
    time_to_exit_mins: Optional[int] = None
    arrival_terminal: Optional[str] = None
    departure_terminal: Optional[str] = None
    user_rating: Optional[int] = Field(None,ge=1, le=10)
    notes: Optional[str] = None
    