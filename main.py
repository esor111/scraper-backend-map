import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY

# Initialize FastAPI app
app = FastAPI(title="Entity Data API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Define Pydantic model for entity data
class EntityData(BaseModel):
    place_id: str
    name: str
    description: Optional[str] = None
    is_spending_on_ads: bool = False
    reviews: int
    rating: float
    competitors: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    can_claim: bool = False
    owner_name: Optional[str] = None
    owner_profile_link: Optional[str] = None
    featured_image: Optional[str] = None
    main_category: Optional[str] = None
    categories: Optional[str] = None
    workday_timing: Optional[str] = None
    is_temporarily_closed: bool = False
    closed_on: Optional[str] = None
    address: Optional[str] = None
    review_keywords: Optional[str] = None
    link: Optional[str] = None
    query: Optional[str] = None

class EntityDataResponse(BaseModel):
    id: str
    place_id: str
    name: str
    description: Optional[str] = None
    is_spending_on_ads: bool = False
    reviews: int
    rating: float
    competitors: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    can_claim: bool = False
    owner_name: Optional[str] = None
    owner_profile_link: Optional[str] = None
    featured_image: Optional[str] = None
    main_category: Optional[str] = None
    categories: Optional[str] = None
    workday_timing: Optional[str] = None
    is_temporarily_closed: bool = False
    closed_on: Optional[str] = None
    address: Optional[str] = None
    review_keywords: Optional[str] = None
    link: Optional[str] = None
    query: Optional[str] = None
    created_at: str
    updated_at: str

@app.get("/")
def read_root():
    return {"message": "Entity Data API is running"}

@app.post("/entity", response_model=EntityDataResponse)
async def create_entity(entity: EntityData):
    try:
        # Insert data into Supabase
        response = supabase.table("entity_data").insert(entity.model_dump()).execute()
        
        # Check if insertion was successful
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to insert data")
        
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/entity/{entity_id}", response_model=EntityDataResponse)
async def get_entity(entity_id: str):
    try:
        # Get entity by ID
        response = supabase.table("entity_data").select("*").eq("id", entity_id).execute()
        
        # Check if entity exists
        if not response.data:
            raise HTTPException(status_code=404, detail="Entity not found")
        
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/entities", response_model=List[EntityDataResponse])
async def get_all_entities():
    try:
        # Get all entities
        response = supabase.table("entity_data").select("*").execute()
        
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)