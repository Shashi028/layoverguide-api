from fastapi import FastAPI, HTTPException
from routers import airports
from routers import itineraries
from database import supabase
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# Initialize the main FastAPI application
app = FastAPI(title="LayoverGuide API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000","https://layoverguide-frontend.vercel.app/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# YOUR CODE HERE: Tell the 'app' to include the router you just built in airports.py
# Use the app.include_router() method.
app.include_router(airports.router)
app.include_router(itineraries.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the LayoverGuide API"}

class UserLogin(BaseModel):
    email: str
    password: str

@app.post("/login")
async def login(user: UserLogin):
    try:
        auth_response = supabase.auth.sign_in_with_password({'email':user.email,'password':user.password})
        return {"access_token": auth_response.session.access_token}
    except jwt.InvalidTokenError as e:
        print(f"TOKEN ERROR: {e}") # This will print the exact reason to your terminal!
        raise HTTPException(status_code=401, detail="Invalid token")

