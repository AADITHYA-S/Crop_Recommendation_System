from fastapi import Depends, Header, HTTPException
from database.supabase_client import supabase

def get_current_farmer(authorization: str = Header(default=None,alias="Authorization")):
    if authorization is None:
      raise HTTPException(status_code=401,detail="Missing Authorization header")
   
    try:
        authorization = authorization.strip()

        if authorization.startswith("Bearer "):
                token=authorization.split(" ")[1]
        else:
            token=authorization

        response=supabase.auth.get_user(token)
        user=response.user

        if user is None:
            raise HTTPException(status_code=401,detail="Invalid or expire")
        
        # print(user)
        return user
   
    except  Exception as e:
        print("Auth error:",e)
        raise HTTPException(status_code=401,detail="Invalid Supabase token")
    