import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
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
    is_spending_on_ads: Optional[bool] = None
    reviews: Optional[int] = None
    rating: Optional[float] = None
    competitors: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    can_claim: Optional[bool] = None
    owner_name: Optional[str] = None
    owner_profile_link: Optional[str] = None
    featured_image: Optional[str] = None
    main_category: Optional[str] = None
    uploaded_image: Optional[bool] = False
    images: List[str] = Field(default_factory=list)
    folder_name: Optional[str] = None
    created_at: Optional[datetime] = None

class EntityDataWithFolder(EntityData):
    folderDir: Optional[str] = None
    link: Optional[str] = None
    query: Optional[str] = None

class EntityDataResponse(BaseModel):
    id: str
    place_id: str
    name: str
    description: Optional[str] = None
    is_spending_on_ads: Optional[bool] = False
    reviews: int
    rating: float
    competitors: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    can_claim: Optional[bool] = False
    owner_name: Optional[str] = None
    owner_profile_link: Optional[str] = None
    featured_image: Optional[str] = None
    main_category: Optional[str] = None
    categories: Optional[str] = None
    workday_timing: Optional[str] = None
    is_temporarily_closed: Optional[bool] = False
    closed_on: Optional[str] = None
    address: Optional[str] = None
    review_keywords: Optional[str] = None
    uploaded_image: Optional[bool] = False
    images: List[str] = Field(default_factory=list)
    link: Optional[str] = None
    query: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

@app.get("/")
def read_root():
    return {"message": "Entity Data API is running"}

@app.post("/entity", response_model=EntityDataResponse)
async def create_entity(entity: EntityData):
    try:
        # Insert data into Supabase
        payload = entity.model_dump()
        # Convert datetime objects to ISO strings for JSON serialization
        if isinstance(payload.get("created_at"), datetime):
            payload["created_at"] = payload["created_at"].isoformat()
        if payload.get("created_at") is None:
            payload["created_at"] = datetime.utcnow().isoformat()
        if isinstance(payload.get("updated_at"), datetime):
            payload["updated_at"] = payload["updated_at"].isoformat()
        if payload.get("updated_at") is None:
            payload["updated_at"] = datetime.utcnow().isoformat()
        if payload.get("uploaded_image") is None:
            payload["uploaded_image"] = False
        if payload.get("images") is None:
            payload["images"] = []
        response = supabase.table("entity_data").insert(payload).execute()
        
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

@app.get("/entities", response_model=List[EntityDataWithFolder])
async def get_all_entities(
    page: int = Query(1, ge=1, description="Page number (starting from 1)"),
    take: int = Query(10, ge=1, le=100, description="Number of items per page"),
    checkimages: Optional[bool] = Query(None, description="Filter entities with empty images array"),
    name: Optional[str] = Query(None, description="Filter entities by name (case-insensitive partial match)"),
    created_from: Optional[str] = Query(None, description="Start date for created_at filter (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)"),
    created_to: Optional[str] = Query(None, description="End date for created_at filter (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)")
):
    """
    Returns a paginated list of businesses with optional filters:
    - checkimages: if True, returns only entities with empty images array
    - name: case-insensitive partial name search
    - created_from/created_to: filter by created_at date range
    """
    base_dir = "C:\\Users\\ishwor\\Desktop\\kaha\\scraper\\images"
    limit = take
    start = (page - 1) * limit
    end = start + limit - 1

    try:
        # Start building the query
        query = supabase.table("entity_data").select("*")
        
        # Apply name filter using ilike for case-insensitive partial matching
        if name:
            # ilike performs case-insensitive pattern matching with wildcards
            query = query.ilike("name", f"%{name}%")
        
        # Apply date range filters
        if created_from:
            try:
                # Try to parse the date string
                if len(created_from) == 10:  # YYYY-MM-DD format
                    created_from_dt = datetime.strptime(created_from, "%Y-%m-%d")
                else:  # YYYY-MM-DD HH:MM:SS format
                    created_from_dt = datetime.strptime(created_from, "%Y-%m-%d %H:%M:%S")
                query = query.gte("created_at", created_from_dt.isoformat())
            except ValueError:
                raise HTTPException(
                    status_code=400, 
                    detail="Invalid created_from date format. Use YYYY-MM-DD or YYYY-MM-DD HH:MM:SS"
                )
        
        if created_to:
            try:
                # Try to parse the date string
                if len(created_to) == 10:  # YYYY-MM-DD format
                    created_to_dt = datetime.strptime(created_to, "%Y-%m-%d")
                    # Set to end of day if only date is provided
                    created_to_dt = created_to_dt.replace(hour=23, minute=59, second=59)
                else:  # YYYY-MM-DD HH:MM:SS format
                    created_to_dt = datetime.strptime(created_to, "%Y-%m-%d %H:%M:%S")
                query = query.lte("created_at", created_to_dt.isoformat())
            except ValueError:
                raise HTTPException(
                    status_code=400, 
                    detail="Invalid created_to date format. Use YYYY-MM-DD or YYYY-MM-DD HH:MM:SS"
                )
        
        # Apply pagination
        query = query.range(start, end)
        
        # Execute the query
        response = query.execute()

        # Apply checkimages filter in Python (since PostgreSQL JSON array filtering is complex)
        filtered_data = response.data
        if checkimages is True:
            # Filter for entities with empty or null images array
            filtered_data = [
                record for record in response.data 
                if not record.get("images") or len(record.get("images", [])) == 0
            ]
        elif checkimages is False:
            # Filter for entities with non-empty images array
            filtered_data = [
                record for record in response.data 
                if record.get("images") and len(record.get("images", [])) > 0
            ]

        # Add folderDir to each record
        for record in filtered_data:
            if record.get("folder_name"):
                record["folderDir"] = os.path.join(base_dir, record["folder_name"])
            else:
                record["folderDir"] = None

        return filtered_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/create-folders", response_model=List[EntityDataWithFolder])
def create_folders(page: int = 1, take: int = 10):
    """
    Fetches businesses with an empty folder_name, generates a folder name based on
    the business name and address, updates the database, and returns the updated
    business data including a new folderDir path.
    """
    base_dir = "C:\\Users\\ishwor\\Desktop\\kaha\\scraper\\images"  # Hardcoded base directory

    try:
        # 1. Get all businesses that have a null folder_name
        limit = take
        start = (page - 1) * limit
        end = start + limit - 1
        response = (
            supabase.table("entity_data")
            .select("*")
            .is_("folder_name", "null")
            .range(start, end)
            .execute()
        )

        if not response.data:
            return []

        updated_businesses_for_response = []

        for business in response.data:
            # 2. For each business, create folder_name
            if not business.get('name') or not business.get('address'):
                continue

            # Sanitize name and address for folder name
            name_part = "".join(business['name'].lower().split())
            address_part = "".join(business['address'].lower().split(',')[0].split())
            folder_name = f"{name_part}_{address_part}"

            # Update the folder_name in the database
            update_response = supabase.table("entity_data").update({"folder_name": folder_name}).eq("place_id", business["place_id"]).execute()

            if update_response.data:
                updated_record = update_response.data[0]
                updated_record['folderDir'] = os.path.join(base_dir, folder_name)
                updated_businesses_for_response.append(updated_record)

        return updated_businesses_for_response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)