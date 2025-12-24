from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt
from bson import ObjectId

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Configuration
SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Models
class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class Beach(BaseModel):
    id: str
    name: str

class BeachPost(BaseModel):
    id: str
    beach_id: str
    name: str

class Inform2Submission(BaseModel):
    date: str
    beach_name: str
    hour: int
    minute: int
    person_name: str
    age: int
    postal_code: str
    incidences: List[str]
    observations: str

class Inform4Submission(BaseModel):
    date: str
    beach_name: str
    hour: int
    minute: int
    wind_speed: float
    temperature: float
    wave_height: float

# Helper functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

# Auth routes
@api_router.post("/auth/register")
async def register(user: UserRegister):
    # Check if user exists
    existing_user = await db.users.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    new_user = {
        "username": user.username,
        "password_hash": hashed_password,
        "created_at": datetime.utcnow()
    }
    await db.users.insert_one(new_user)
    return {"message": "User created successfully"}

@api_router.post("/auth/login", response_model=Token)
async def login(user: UserLogin):
    # Find user
    db_user = await db.users.find_one({"username": user.username})
    if not db_user or not verify_password(user.password, db_user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# Beach routes
@api_router.get("/beaches", response_model=List[Beach])
async def get_beaches(current_user: str = Depends(get_current_user)):
    beaches = await db.beaches.find().to_list(1000)
    return [{"id": str(beach["_id"]), "name": beach["name"]} for beach in beaches]

@api_router.get("/beach-posts/{beach_id}", response_model=List[BeachPost])
async def get_beach_posts(beach_id: str, current_user: str = Depends(get_current_user)):
    try:
        beach_posts = await db.beach_posts.find({"beach_id": beach_id}).to_list(1000)
        return [
            {
                "id": str(post["_id"]),
                "beach_id": post["beach_id"],
                "name": post["name"]
            }
            for post in beach_posts
        ]
    except Exception as e:
        logger.error(f"Error fetching beach posts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching beach posts"
        )

# Inform routes
@api_router.post("/inform2")
async def submit_inform2(data: Inform2Submission, current_user: str = Depends(get_current_user)):
    try:
        submission = {
            **data.dict(),
            "username": current_user,
            "created_at": datetime.utcnow()
        }
        result = await db.inform2_submissions.insert_one(submission)
        return {"message": "Inform 2 submitted successfully", "id": str(result.inserted_id)}
    except Exception as e:
        logger.error(f"Error submitting Inform 2: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error submitting Inform 2"
        )

@api_router.post("/inform4")
async def submit_inform4(data: Inform4Submission, current_user: str = Depends(get_current_user)):
    try:
        submission = {
            **data.dict(),
            "username": current_user,
            "created_at": datetime.utcnow()
        }
        result = await db.inform4_submissions.insert_one(submission)
        return {"message": "Inform 4 submitted successfully", "id": str(result.inserted_id)}
    except Exception as e:
        logger.error(f"Error submitting Inform 4: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error submitting Inform 4"
        )

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_db_client():
    # Create sample data if collections are empty
    beaches_count = await db.beaches.count_documents({})
    if beaches_count == 0:
        sample_beaches = [
            {"name": "Santa Monica Beach", "created_at": datetime.utcnow()},
            {"name": "Venice Beach", "created_at": datetime.utcnow()},
            {"name": "Malibu Beach", "created_at": datetime.utcnow()},
        ]
        result = await db.beaches.insert_many(sample_beaches)
        
        # Create beach posts for each beach
        beach_posts = []
        for i, beach_id in enumerate(result.inserted_ids):
            beach_posts.extend([
                {"beach_id": str(beach_id), "name": f"Post A", "created_at": datetime.utcnow()},
                {"beach_id": str(beach_id), "name": f"Post B", "created_at": datetime.utcnow()},
                {"beach_id": str(beach_id), "name": f"Post C", "created_at": datetime.utcnow()},
            ])
        await db.beach_posts.insert_many(beach_posts)
        logger.info("Sample beaches and beach posts created")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
