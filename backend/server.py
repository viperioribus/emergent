from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import aiomysql
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt
import json

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MySQL connection configuration
MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
MYSQL_PORT = int(os.environ.get('MYSQL_PORT', '3306'))
MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
MYSQL_DB = os.environ.get('MYSQL_DB', 'beach_informs')

# JWT Configuration
SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Create the main app
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database connection pool
db_pool = None

# Models
class UserLogin(BaseModel):
    login: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class Beach(BaseModel):
    id: int
    name: str

class BeachPost(BaseModel):
    id: int
    beach_id: int
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
    # For existing users with plain text passwords, compare directly
    # For new users, use bcrypt
    if hashed_password.startswith('$2b$'):
        return pwd_context.verify(plain_password, hashed_password)
    else:
        return plain_password == hashed_password

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

async def get_db_connection():
    """Get a connection from the pool"""
    return await db_pool.acquire()

async def release_db_connection(conn):
    """Release connection back to the pool"""
    db_pool.release(conn)

# Auth routes
@api_router.post("/auth/login", response_model=Token)
async def login(user: UserLogin):
    conn = await get_db_connection()
    try:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(
                "SELECT * FROM usuarios WHERE login = %s",
                (user.login,)
            )
            db_user = await cursor.fetchone()
            
            if not db_user or not verify_password(user.password, db_user['password']):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect login or password"
                )
            
            # Create access token
            access_token = create_access_token(data={"sub": user.login})
            return {"access_token": access_token, "token_type": "bearer"}
    finally:
        release_db_connection(conn)

# Beach routes
@api_router.get("/beaches", response_model=List[Beach])
async def get_beaches(current_user: str = Depends(get_current_user)):
    conn = await get_db_connection()
    try:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute("SELECT id, name FROM beaches ORDER BY name")
            beaches = await cursor.fetchall()
            return beaches
    finally:
        release_db_connection(conn)

@api_router.get("/beach-posts/{beach_id}", response_model=List[BeachPost])
async def get_beach_posts(beach_id: int, current_user: str = Depends(get_current_user)):
    conn = await get_db_connection()
    try:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(
                "SELECT id, beach_id, name FROM beach_posts WHERE beach_id = %s ORDER BY name",
                (beach_id,)
            )
            posts = await cursor.fetchall()
            return posts
    except Exception as e:
        logger.error(f"Error fetching beach posts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching beach posts"
        )
    finally:
        release_db_connection(conn)

# Inform routes
@api_router.post("/inform2")
async def submit_inform2(data: Inform2Submission, current_user: str = Depends(get_current_user)):
    conn = await get_db_connection()
    try:
        async with conn.cursor() as cursor:
            # Convert list of incidences to JSON string
            incidences_json = json.dumps(data.incidences)
            
            await cursor.execute(
                """INSERT INTO inform2_submissions 
                   (date, beach_name, hour, minute, person_name, age, postal_code, 
                    incidences, observations, username, created_at)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (data.date, data.beach_name, data.hour, data.minute, data.person_name,
                 data.age, data.postal_code, incidences_json, data.observations,
                 current_user, datetime.utcnow())
            )
            await conn.commit()
            return {"message": "Inform 2 submitted successfully", "id": cursor.lastrowid}
    except Exception as e:
        logger.error(f"Error submitting Inform 2: {e}")
        await conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error submitting Inform 2"
        )
    finally:
        release_db_connection(conn)

@api_router.post("/inform4")
async def submit_inform4(data: Inform4Submission, current_user: str = Depends(get_current_user)):
    conn = await get_db_connection()
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(
                """INSERT INTO inform4_submissions 
                   (date, beach_name, hour, minute, wind_speed, temperature, 
                    wave_height, username, created_at)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (data.date, data.beach_name, data.hour, data.minute, data.wind_speed,
                 data.temperature, data.wave_height, current_user, datetime.utcnow())
            )
            await conn.commit()
            return {"message": "Inform 4 submitted successfully", "id": cursor.lastrowid}
    except Exception as e:
        logger.error(f"Error submitting Inform 4: {e}")
        await conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error submitting Inform 4"
        )
    finally:
        release_db_connection(conn)

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
async def startup_db():
    global db_pool
    # Create connection pool
    db_pool = await aiomysql.create_pool(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        db=MYSQL_DB,
        minsize=1,
        maxsize=10,
        autocommit=False
    )
    logger.info("MySQL connection pool created")
    
    # Initialize tables and sample data
    conn = await get_db_connection()
    try:
        async with conn.cursor() as cursor:
            # Create beaches table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS beaches (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_name (name)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Create beach_posts table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS beach_posts (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    beach_id INT NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_beach_id (beach_id),
                    FOREIGN KEY (beach_id) REFERENCES beaches(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Create inform2_submissions table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS inform2_submissions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    date DATE NOT NULL,
                    beach_name VARCHAR(200) NOT NULL,
                    hour INT NOT NULL,
                    minute INT NOT NULL,
                    person_name VARCHAR(100) NOT NULL,
                    age INT NOT NULL,
                    postal_code VARCHAR(20) NOT NULL,
                    incidences TEXT NOT NULL,
                    observations TEXT,
                    username VARCHAR(50) NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_date (date),
                    INDEX idx_username (username)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Create inform4_submissions table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS inform4_submissions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    date DATE NOT NULL,
                    beach_name VARCHAR(200) NOT NULL,
                    hour INT NOT NULL,
                    minute INT NOT NULL,
                    wind_speed DECIMAL(5,2) NOT NULL,
                    temperature DECIMAL(5,2) NOT NULL,
                    wave_height DECIMAL(5,2) NOT NULL,
                    username VARCHAR(50) NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_date (date),
                    INDEX idx_username (username)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            await conn.commit()
            
            # Check if we need to insert sample data
            await cursor.execute("SELECT COUNT(*) as count FROM beaches")
            result = await cursor.fetchone()
            
            if result[0] == 0:
                # Insert sample beaches
                await cursor.execute("""
                    INSERT INTO beaches (name) VALUES 
                    ('Santa Monica Beach'),
                    ('Venice Beach'),
                    ('Malibu Beach')
                """)
                
                # Get beach IDs
                await cursor.execute("SELECT id FROM beaches ORDER BY id")
                beach_ids = await cursor.fetchall()
                
                # Insert beach posts for each beach
                for beach_id_tuple in beach_ids:
                    beach_id = beach_id_tuple[0]
                    await cursor.execute("""
                        INSERT INTO beach_posts (beach_id, name) VALUES 
                        (%s, 'Post A'),
                        (%s, 'Post B'),
                        (%s, 'Post C')
                    """, (beach_id, beach_id, beach_id))
                
                await conn.commit()
                logger.info("Sample beaches and beach posts created")
    finally:
        release_db_connection(conn)

@app.on_event("shutdown")
async def shutdown_db():
    global db_pool
    if db_pool:
        db_pool.close()
        await db_pool.wait_closed()
        logger.info("MySQL connection pool closed")
