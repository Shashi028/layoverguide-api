from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from database import supabase  # <-- We import your existing Supabase client!

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    
    try:
        # We hand the token directly to Supabase to verify it for us
        user_response = supabase.auth.get_user(token)
        
        # If the token is fake or expired, the line above will crash and go to the except block.
        # If it is valid, Supabase hands us back the user object!
        return user_response.user.id
        
    except Exception as e:
        print(f"Supabase Auth Error: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid token")