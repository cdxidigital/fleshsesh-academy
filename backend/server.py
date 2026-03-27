from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import jwt
import bcrypt

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'fleshsesh-academy-secret-key-2024')
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Security
security = HTTPBearer()

# Create the main app
app = FastAPI(title="Fleshsesh Academy API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# ============== MODELS ==============

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    email: str
    name: str
    xp: int = 0
    level: int = 1
    tokens: int = 100
    subscription_tier: str = "free"
    completed_lessons: List[str] = []
    created_at: str

class AuthResponse(BaseModel):
    token: str
    user: UserResponse

class LessonProgress(BaseModel):
    lesson_id: str

class Course(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    level: int
    title: str
    description: str
    modules: int
    lessons: int
    image_url: str
    skills: List[str]
    instructor: str

class Lesson(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    course_id: str
    module_number: int
    lesson_number: int
    title: str
    description: str
    content: str
    xp_reward: int = 25
    duration_minutes: int = 5

class Instructor(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    name: str
    title: str
    specialty: str
    description: str
    personality: Optional[str] = None
    teaching_style: Optional[str] = None
    image_url: str

# ============== HELPER FUNCTIONS ==============

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_token(user_id: str) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = await db.users.find_one({"id": user_id}, {"_id": 0, "password": 0})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ============== SEED DATA ==============

COURSES_DATA = [
    {
        "id": "level-1",
        "level": 1,
        "title": "Foundations of Presence",
        "description": "Build self-awareness, emotional literacy, and understand your desire patterns. Master body language basics and consent foundations.",
        "modules": 5,
        "lessons": 50,
        "image_url": "https://images.pexels.com/photos/5931495/pexels-photo-5931495.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "skills": ["Self-Awareness", "Body Language", "Emotional Literacy", "Boundaries"],
        "instructor": "Aria Wren"
    },
    {
        "id": "level-2",
        "level": 2,
        "title": "Attraction Dynamics",
        "description": "Master social energy, flirting fundamentals, and the art of playful tension. Learn to navigate first dates and handle rejection gracefully.",
        "modules": 5,
        "lessons": 50,
        "image_url": "https://images.pexels.com/photos/1600128/pexels-photo-1600128.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "skills": ["Flirting", "Social Energy", "Texting", "First Dates"],
        "instructor": "Marcus Vale"
    },
    {
        "id": "level-3",
        "level": 3,
        "title": "Connection",
        "description": "Develop emotional depth, build trust, and master sexual communication. Navigate desire differences and create lasting intimacy rituals.",
        "modules": 5,
        "lessons": 50,
        "image_url": "https://images.unsplash.com/photo-1765854894510-7bb4cc0d88eb?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85",
        "skills": ["Emotional Depth", "Trust Building", "Sexual Communication", "Conflict Resolution"],
        "instructor": "Aria Wren"
    },
    {
        "id": "level-4",
        "level": 4,
        "title": "Intimacy Mastery",
        "description": "Unlock sensual awareness, touch mastery, and arousal communication. Learn aftercare rituals and overcome performance anxiety.",
        "modules": 5,
        "lessons": 50,
        "image_url": "https://images.unsplash.com/photo-1769414702897-29a55edc6bbc?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85",
        "skills": ["Sensual Awareness", "Touch Mastery", "Arousal Control", "Aftercare"],
        "instructor": "Luca Amore"
    },
    {
        "id": "level-5",
        "level": 5,
        "title": "Erotic Exploration",
        "description": "Explore fantasy psychology, roleplay creation, and erotic storytelling. Learn sensory play and introduce novelty safely.",
        "modules": 5,
        "lessons": 50,
        "image_url": "https://images.pexels.com/photos/1493295/pexels-photo-1493295.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "skills": ["Fantasy Design", "Roleplay", "Erotic Storytelling", "Sensory Play"],
        "instructor": "Nyx"
    },
    {
        "id": "level-6",
        "level": 6,
        "title": "Positions & Physical Mastery",
        "description": "Master anatomy of pleasure, explore positions for all bodies, and develop stamina. Includes inclusive variations and body-positive practice.",
        "modules": 5,
        "lessons": 50,
        "image_url": "https://images.unsplash.com/photo-1771433085746-9adf1294c7ad?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85",
        "skills": ["Anatomy", "Positions", "Stamina", "Body Mechanics"],
        "instructor": "Luca Amore"
    },
    {
        "id": "level-7",
        "level": 7,
        "title": "Power Dynamics & Kink",
        "description": "Learn consent architecture, impact play safety, and D/s psychology. Master negotiation scripts and ethical kink practice.",
        "modules": 5,
        "lessons": 50,
        "image_url": "https://images.pexels.com/photos/5631041/pexels-photo-5631041.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "skills": ["Consent Architecture", "Power Exchange", "Scene Design", "Negotiation"],
        "instructor": "Nyx"
    },
    {
        "id": "level-8",
        "level": 8,
        "title": "Relationship Strategy",
        "description": "Design relationship structures, navigate monogamy and non-monogamy, and build conflict repair systems. Master long-term relationship architecture.",
        "modules": 5,
        "lessons": 50,
        "image_url": "https://images.unsplash.com/photo-1763391275169-d686f6d46f17?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85",
        "skills": ["Relationship Design", "Agreements", "Repair Rituals", "Growth Planning"],
        "instructor": "Dr. Evelyn Hart"
    },
    {
        "id": "level-9",
        "level": 9,
        "title": "Digital Intimacy & Modern Dating",
        "description": "Master online dating, build authentic digital connections, and navigate modern relationship dynamics across platforms.",
        "modules": 5,
        "lessons": 50,
        "image_url": "https://images.unsplash.com/photo-1769414704400-d4f7549bcfda?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85",
        "skills": ["Online Dating", "Digital Communication", "App Strategy", "Video Dates"],
        "instructor": "Kai Storm"
    },
    {
        "id": "level-10",
        "level": 10,
        "title": "Capstone Mastery Paths",
        "description": "Choose your specialization: Relationship Architect, Erotic Explorer, Power Dynamics Master, or Tantric Intimacy. Includes teaching others.",
        "modules": 5,
        "lessons": 50,
        "image_url": "https://images.unsplash.com/photo-1763677594421-f58e50cce64d?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85",
        "skills": ["Specialization", "Mentoring", "Advanced Practice", "Integration"],
        "instructor": "All Faculty"
    }
]

INSTRUCTORS_DATA = [
    {
        "id": "marcus-vale",
        "name": "Marcus Vale",
        "title": "Attraction & Social Dynamics Coach",
        "specialty": "Attraction, Flirting, Social Energy, Confidence Building",
        "description": "Former social anxiety sufferer turned charisma expert. Marcus teaches authentic confidence without manipulation, focusing on ethical attraction and genuine connection.",
        "personality": "Warm, encouraging, and direct. Uses humor to ease tension and real-world examples from his own journey. Never judges—celebrates every small win.",
        "teaching_style": "Socratic questioning combined with practical exercises. Assigns 'field missions' to practice skills in low-stakes environments. Provides detailed feedback on approach scenarios.",
        "image_url": "https://images.pexels.com/photos/6956149/pexels-photo-6956149.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"
    },
    {
        "id": "nyx",
        "name": "Nyx",
        "title": "Power Dynamics & Kink Educator",
        "specialty": "BDSM, Power Exchange, Consent Architecture, Scene Design",
        "description": "A mysterious and commanding presence, Nyx guides learners through the psychology of power dynamics with an unwavering focus on safety, consent, and ethical exploration.",
        "personality": "Calm authority with unexpected warmth. Speaks in measured, deliberate tones. Has zero tolerance for boundary violations but infinite patience for genuine questions.",
        "teaching_style": "Safety-first demonstrations, detailed negotiation frameworks, and progressive skill-building. Uses case studies and 'what-if' scenarios to prepare for edge cases.",
        "image_url": "https://images.pexels.com/photos/5631041/pexels-photo-5631041.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"
    },
    {
        "id": "aria-wren",
        "name": "Aria Wren",
        "title": "Emotional Intelligence & Connection Expert",
        "specialty": "Emotional Depth, Trust Building, Relationship Strategy, Attachment Healing",
        "description": "Warm, insightful, and deeply empathetic. Aria specializes in building emotional safety, navigating vulnerability, and creating lasting intimate connections.",
        "personality": "Gentle yet incisive. Creates immediate psychological safety. Has an uncanny ability to name emotions before learners can articulate them.",
        "teaching_style": "Reflective journaling prompts, guided visualizations, and attachment-informed coaching. Helps identify patterns and gently challenges self-limiting beliefs.",
        "image_url": "https://images.unsplash.com/photo-1763906803356-c4c2c83dc012?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85"
    },
    {
        "id": "luca-amore",
        "name": "Luca Amore",
        "title": "Physical Intimacy & Pleasure Guide",
        "specialty": "Touch Mastery, Positions, Sensual Awareness, Anatomy of Pleasure",
        "description": "Body-positive advocate and pleasure researcher. Luca teaches the art of physical connection with scientific precision and playful energy, celebrating all bodies.",
        "personality": "Playful, scientific, and enthusiastically body-positive. Makes anatomy discussions feel natural and fun. Normalizes all bodies and desires.",
        "teaching_style": "Combines neuroscience with practical technique. Uses anatomical models, guided self-exploration exercises, and partner communication scripts.",
        "image_url": "https://images.unsplash.com/photo-1689218744786-9546da7b6873?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85"
    },
    {
        "id": "dr-evelyn-hart",
        "name": "Dr. Evelyn Hart",
        "title": "Relationship Architect & Therapist",
        "specialty": "Long-term Relationships, Conflict Resolution, Relationship Design, Couples Therapy",
        "description": "Licensed relationship therapist with 20 years of AI-synthesized clinical experience. Dr. Hart helps design sustainable relationship structures and repair damaged connections.",
        "personality": "Professionally warm with academic precision. Balances validation with accountability. Never takes sides but illuminates blind spots.",
        "teaching_style": "Evidence-based interventions, structured communication frameworks (like Gottman Method), and relationship 'health audits'. Assigns couple exercises and individual reflection.",
        "image_url": "https://images.pexels.com/photos/1493295/pexels-photo-1493295.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"
    },
    {
        "id": "kai-storm",
        "name": "Kai Storm",
        "title": "Digital Intimacy & Modern Dating Specialist",
        "specialty": "Online Dating, Texting, Video Dates, Digital Boundaries, Sexting Safety",
        "description": "Gen-Z native who decoded the algorithms of modern romance. Kai teaches authentic connection in digital spaces while maintaining safety and boundaries.",
        "personality": "Energetic, tech-savvy, and refreshingly honest. Speaks the language of dating apps fluently. Keeps it real about the challenges of modern dating.",
        "teaching_style": "Profile reviews, message coaching, and app strategy sessions. Analyzes screenshots, suggests openers, and helps craft authentic online personas.",
        "image_url": "https://images.unsplash.com/photo-1619241805829-34fb64299391?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85"
    },
    {
        "id": "maya-tantra",
        "name": "Maya Oasis",
        "title": "Tantric Intimacy & Breathwork Guide",
        "specialty": "Tantra, Breathwork, Energy Connection, Mindful Sexuality, Sacred Intimacy",
        "description": "Trained in Eastern and Western traditions of sacred sexuality. Maya weaves together ancient wisdom and modern neuroscience to create transcendent intimate experiences.",
        "personality": "Serene, mystical yet grounded. Speaks slowly and intentionally. Creates ritualistic containers for learning. Deeply spiritual without being preachy.",
        "teaching_style": "Guided meditations, breathwork practices, and energy awareness exercises. Emphasizes presence, intention-setting, and the spiritual dimensions of connection.",
        "image_url": "https://images.unsplash.com/photo-1771433085746-9adf1294c7ad?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85"
    },
    {
        "id": "rex-sterling",
        "name": "Rex Sterling",
        "title": "Masculinity & Vulnerability Coach",
        "specialty": "Masculine Energy, Vulnerability, Leadership in Intimacy, Men's Issues",
        "description": "Former 'tough guy' who discovered strength in softness. Rex helps men (and masculine-identifying people) integrate power with emotional availability and authentic expression.",
        "personality": "Gruff exterior, surprisingly tender core. Speaks from hard-won experience. Challenges toxic patterns while honoring healthy masculine energy.",
        "teaching_style": "Direct confrontation of limiting beliefs, shame resilience exercises, and permission-giving for emotional expression. Uses his own transformation story as teaching material.",
        "image_url": "https://images.unsplash.com/photo-1595790753283-3c164baddb72?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85"
    }
]

SAMPLE_LESSONS = [
    {
        "id": "lesson-1-1-1",
        "course_id": "level-1",
        "module_number": 1,
        "lesson_number": 1,
        "title": "What Intimacy Means to You",
        "description": "Explore your personal definition of intimacy and discover what truly matters in your connections.",
        "content": """# What Intimacy Means to You

Welcome to your first lesson at Fleshsesh Academy. Before we can build skills, we need to understand what intimacy means to *you*.

## Reflection Exercise

Take a moment to consider:
- When do you feel most connected to another person?
- What does emotional intimacy look like vs physical intimacy?
- What past experiences have shaped your view of intimacy?

## Key Insight

Intimacy isn't one-size-fits-all. Your unique needs, experiences, and desires shape what meaningful connection looks like for you.

## Action Step

Write down three moments in your life when you felt deeply connected to someone. What made those moments special?""",
        "xp_reward": 25,
        "duration_minutes": 5
    },
    {
        "id": "lesson-1-1-2",
        "course_id": "level-1",
        "module_number": 1,
        "lesson_number": 2,
        "title": "Spotting Your Attraction Patterns",
        "description": "Identify recurring patterns in who you're attracted to and why.",
        "content": """# Spotting Your Attraction Patterns

Understanding your attraction patterns is the first step to making conscious choices about who you pursue and why.

## The Pattern Recognition Exercise

Think about your last 3-5 significant attractions or relationships:
- What traits did they share?
- What initially drew you to them?
- How did these connections typically unfold?

## Common Patterns

- Pursuing unavailable partners
- Attraction to "projects" or fixers
- Seeking validation through attraction
- Confusing intensity for compatibility

## Key Insight

Patterns aren't inherently bad—they're data. Understanding them helps you make conscious choices rather than repeating unconscious cycles.""",
        "xp_reward": 25,
        "duration_minutes": 5
    },
    {
        "id": "lesson-2-1-1",
        "course_id": "level-2",
        "module_number": 1,
        "lesson_number": 1,
        "title": "Switching On Social Warmth Intentionally",
        "description": "Learn to consciously activate your natural warmth and charisma in social situations.",
        "content": """# Switching On Social Warmth Intentionally

Social warmth isn't just something you have or don't have—it's a skill you can intentionally activate.

## The Warmth Switch

Before entering any social situation:
1. Take three deep breaths
2. Recall a moment of genuine connection
3. Soften your facial expression
4. Open your body language

## Why This Works

Your nervous system responds to your intentional state shifts. When you feel warm internally, you project warmth externally.

## Practice Exercise

Before your next social interaction, take 30 seconds to activate your warmth. Notice how people respond differently.""",
        "xp_reward": 25,
        "duration_minutes": 5
    }
]

# ============== AUTH ROUTES ==============

@api_router.post("/auth/register", response_model=AuthResponse)
async def register(user_data: UserCreate):
    # Check if user exists
    existing = await db.users.find_one({"email": user_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    user_doc = {
        "id": user_id,
        "email": user_data.email,
        "name": user_data.name,
        "password": hash_password(user_data.password),
        "xp": 0,
        "level": 1,
        "tokens": 100,
        "subscription_tier": "free",
        "completed_lessons": [],
        "created_at": now
    }
    
    await db.users.insert_one(user_doc)
    
    token = create_token(user_id)
    user_response = UserResponse(
        id=user_id,
        email=user_data.email,
        name=user_data.name,
        xp=0,
        level=1,
        tokens=100,
        subscription_tier="free",
        completed_lessons=[],
        created_at=now
    )
    
    return AuthResponse(token=token, user=user_response)

@api_router.post("/auth/login", response_model=AuthResponse)
async def login(credentials: UserLogin):
    user = await db.users.find_one({"email": credentials.email})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not verify_password(credentials.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_token(user["id"])
    user_response = UserResponse(
        id=user["id"],
        email=user["email"],
        name=user["name"],
        xp=user.get("xp", 0),
        level=user.get("level", 1),
        tokens=user.get("tokens", 100),
        subscription_tier=user.get("subscription_tier", "free"),
        completed_lessons=user.get("completed_lessons", []),
        created_at=user["created_at"]
    )
    
    return AuthResponse(token=token, user=user_response)

@api_router.get("/auth/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return UserResponse(**current_user)

# ============== COURSES ROUTES ==============

@api_router.get("/courses", response_model=List[Course])
async def get_courses():
    return COURSES_DATA

@api_router.get("/courses/{course_id}", response_model=Course)
async def get_course(course_id: str):
    for course in COURSES_DATA:
        if course["id"] == course_id:
            return course
    raise HTTPException(status_code=404, detail="Course not found")

# ============== LESSONS ROUTES ==============

@api_router.get("/courses/{course_id}/lessons", response_model=List[Lesson])
async def get_lessons(course_id: str):
    lessons = [l for l in SAMPLE_LESSONS if l["course_id"] == course_id]
    return lessons

@api_router.get("/lessons/{lesson_id}", response_model=Lesson)
async def get_lesson(lesson_id: str):
    for lesson in SAMPLE_LESSONS:
        if lesson["id"] == lesson_id:
            return lesson
    raise HTTPException(status_code=404, detail="Lesson not found")

@api_router.post("/lessons/{lesson_id}/complete")
async def complete_lesson(lesson_id: str, current_user: dict = Depends(get_current_user)):
    # Find lesson
    lesson = None
    for l in SAMPLE_LESSONS:
        if l["id"] == lesson_id:
            lesson = l
            break
    
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    user_id = current_user["id"]
    completed = current_user.get("completed_lessons", [])
    
    if lesson_id in completed:
        return {"message": "Lesson already completed", "xp_earned": 0}
    
    # Update user progress
    new_xp = current_user.get("xp", 0) + lesson["xp_reward"]
    new_level = (new_xp // 500) + 1  # Level up every 500 XP
    completed.append(lesson_id)
    
    await db.users.update_one(
        {"id": user_id},
        {"$set": {
            "xp": new_xp,
            "level": new_level,
            "completed_lessons": completed
        }}
    )
    
    return {
        "message": "Lesson completed!",
        "xp_earned": lesson["xp_reward"],
        "total_xp": new_xp,
        "level": new_level
    }

# ============== INSTRUCTORS ROUTES ==============

@api_router.get("/instructors", response_model=List[Instructor])
async def get_instructors():
    return INSTRUCTORS_DATA

@api_router.get("/instructors/{instructor_id}", response_model=Instructor)
async def get_instructor(instructor_id: str):
    for instructor in INSTRUCTORS_DATA:
        if instructor["id"] == instructor_id:
            return instructor
    raise HTTPException(status_code=404, detail="Instructor not found")

# ============== HEALTH CHECK ==============

@api_router.get("/")
async def root():
    return {"message": "Fleshsesh Academy API", "status": "running"}

@api_router.get("/health")
async def health_check():
    return {"status": "healthy"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
