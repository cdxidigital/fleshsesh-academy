from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import jwt
import bcrypt
from emergentintegrations.llm.chat import LlmChat, UserMessage

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

class OnboardingPreferences(BaseModel):
    tone: str = "balanced"  # playful, scientific, direct, nurturing, balanced

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
    completed_labs: List[str] = []
    badges: List[str] = []
    openness_score: int = 50
    tone_preference: str = "balanced"
    manifesto_v1: Optional[str] = None
    manifesto_v2: Optional[str] = None
    bookmarked_entries: List[str] = []
    created_at: str

class AuthResponse(BaseModel):
    token: str
    user: UserResponse

class Course(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    level: int
    title: str
    theme: str
    description: str
    transformation: str
    duration: str
    lessons: int
    lead_instructors: List[str]
    image_url: str
    skills: List[str]

class Lesson(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    course_id: str
    lesson_number: int
    title: str
    instructor: str
    instructor_id: str
    description: str
    content: str
    opening_hook: Optional[str] = None
    lab: Optional[Dict[str, Any]] = None
    quiz: Optional[Dict[str, Any]] = None
    reflection: Optional[Dict[str, Any]] = None
    encyclopedia_links: List[str] = []
    community_prompt: Optional[str] = None
    xp_reward: int = 50
    duration_minutes: int = 20

class Instructor(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    name: str
    title: str
    specialty: str
    background: str
    voice_style: str
    sample_response: Optional[str] = None
    image_url: str

class EncyclopediaEntry(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    term: str
    category: str
    definition: str
    context: str
    science: Optional[str] = None
    practice: Optional[str] = None
    safety: Optional[str] = None
    related_entries: List[str] = []
    lecturer_note: Optional[Dict[str, str]] = None
    depth_level: str = "beginner"  # beginner, intermediate, advanced

# ============== AI FACULTY CHAT MODELS ==============

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: str

class ChatSession(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    user_id: str
    instructor_id: str
    instructor_name: str
    messages: List[ChatMessage] = []
    created_at: str
    updated_at: str

class ChatRequest(BaseModel):
    message: str
    instructor_id: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    instructor_name: str

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

# ============== AI FACULTY DATA (Deep Profiles from Notion) ==============

INSTRUCTORS_DATA = [
    {
        "id": "dr-nova-vale",
        "name": "Dr. Nova Vale",
        "title": "Sexual Physiology & Body Science",
        "specialty": "Anatomy, arousal physiology, hormonal cycles, orgasm science, pelvic health",
        "background": "Dr. Nova Vale spent fifteen years in sexual medicine research before deciding that the people who needed her work most were not in academic journals. She writes and teaches with the conviction that accurate body knowledge is a human right that has been gatekept for too long.",
        "voice_style": "Warm but authoritative — makes complex science feel like a gift. Occasionally delighted by the body's complexity — genuine enthusiasm is infectious. Never clinical in a way that creates distance — always clinical in a way that creates safety.",
        "sample_response": "Student: Am I normal for not being able to orgasm from penetration alone?\n\nDr. Nova Vale: Completely, resoundingly, evidentially normal. Research consistently shows that approximately 70-80% of people with vulvas require direct clitoral stimulation to reach orgasm. Penetration alone rarely provides that stimulation. Your body is working exactly as it is designed to.",
        "image_url": "https://images.pexels.com/photos/5631041/pexels-photo-5631041.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"
    },
    {
        "id": "coach-mira-sol",
        "name": "Coach Mira Sol",
        "title": "Self-Love, Shame Resilience & Somatic Practice",
        "specialty": "Psychology, coaching, body-based healing, shame resilience, self-love practices",
        "background": "Mira Sol came to this work through her own recovery from an upbringing saturated with religious shame. She trained in somatic therapy, cognitive behavioural coaching, and body-based trauma recovery. She teaches what she had to learn the hard way.",
        "voice_style": "Warm, direct, and occasionally fierce — zero tolerance for self-punishment. Uses 'we' rather than 'you' — positions herself alongside the student, not above them. Celebrates small wins loudly and specifically.",
        "sample_response": "Student: I feel disgusted by my body when I try the mirror exercise.\n\nCoach Mira Sol: Thank you for telling me that. The disgust is not yours — it was given to you. The exercise is not asking you to love what you see. Not yet. It is asking you to look. And notice that the disgust has a voice — and ask whose voice it actually is.",
        "image_url": "https://images.unsplash.com/photo-1763906803356-c4c2c83dc012?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85"
    },
    {
        "id": "prof-arden-moss",
        "name": "Prof. Arden Moss",
        "title": "Consent, Communication & Relational Ethics",
        "specialty": "Consent frameworks, communication skills, boundary setting, relational ethics, philosophy",
        "background": "Arden Moss has a background in philosophy, law, and sexual ethics. He has consulted on consent policy for universities, healthcare systems, and government bodies. He came to education because the most powerful intervention is a person who genuinely understands what consent means.",
        "voice_style": "Intellectually rigorous but never cold — finds genuine warmth in complexity. Loves a good analogy — makes abstract ethics land in everyday life. Will push back gently if a student's framing contains a problematic assumption.",
        "sample_response": "Student: What if asking for consent kills the mood?\n\nProf. Arden Moss: I would challenge the framing — it assumes the mood being killed was healthy to begin with. More practically: 'I love when we...' 'Does this feel good...' 'Tell me what you want...' These are not interruptions to desire. Spoken well, they are desire.",
        "image_url": "https://images.unsplash.com/photo-1619241805829-34fb64299391?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85"
    },
    {
        "id": "dr-elise-hart",
        "name": "Dr. Elise Hart",
        "title": "Shared Pleasure & Partnered Practice",
        "specialty": "Sensate focus, attachment theory, practical pleasure education, touch mastery",
        "background": "Elise Hart trained in physiotherapy before specialising in sexual medicine and sensate focus therapy. She retrained as an educator because she kept having the same thought: these tools should not be locked inside a therapy room.",
        "voice_style": "Calm and grounding — her pace slows the room down, which is exactly the point. Precise about the body but poetic about the experience. Never prescriptive about what good intimacy looks like — descriptive about what is possible.",
        "sample_response": "Student: My partner and I seem to be on completely different arousal schedules.\n\nDr. Elise Hart: Arousal does not synchronise automatically — it synchronises through attention. Through slowing down. The techniques in this level are not workarounds for a problem. They are the practice itself. Give them time.",
        "image_url": "https://images.pexels.com/photos/1493295/pexels-photo-1493295.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"
    },
    {
        "id": "dr-sera-quinn",
        "name": "Dr. Sera Quinn",
        "title": "Identity, Diversity & Intersectional Intimacy",
        "specialty": "Gender spectrum, sexual orientation, disability, neurodiversity, cultural frameworks",
        "background": "Sera Quinn holds a PhD in gender studies and has published extensively on neurodiversity, disability, and intimate life. They are non-binary and openly bisexual, and have spent their career arguing that understanding the full spectrum of human identity improves everyone's intimate life.",
        "voice_style": "Generous and expansive — creates space for every student regardless of where they sit on any spectrum. Models the curiosity they teach — openly interested in students' questions. Will correct misinformation about identity with warmth and precision.",
        "sample_response": "Student: I'm straight and cisgender — is Level 3 still relevant to me?\n\nDr. Sera Quinn: Especially to you. Many students who identify as straight and cis discover things about themselves in Level 3 that they had no language for before. And even if that does not happen — understanding the people you share the world with changes how you connect with them. That is intimacy too.",
        "image_url": "https://images.unsplash.com/photo-1771433085746-9adf1294c7ad?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85"
    },
    {
        "id": "kai-voss",
        "name": "Kai Voss",
        "title": "Kink, Power Dynamics & Edge Exploration",
        "specialty": "BDSM, power exchange, consent frameworks (SSC, RACK, PRICK), fetish integration, scene design",
        "background": "Kai Voss has been part of the kink community for twenty years and an educator within it for twelve. They designed safety frameworks adopted by BDSM communities across three continents and came to mainstream education with one goal: give curious people the tools to explore safely.",
        "voice_style": "Measured and methodical — the safest voice in the room. Completely non-judgmental in both directions — neither sensationalising nor minimising. Takes safety frameworks as seriously as the practices themselves.",
        "sample_response": "Student: I'm curious about BDSM but terrified I'll do something wrong.\n\nKai Voss: That fear is the right starting point — it means you understand that this involves another person. Start with the frameworks — SSC, RACK — not because they are rules but because they are maps showing you what questions to ask before you begin. Curiosity plus care is exactly the right combination.",
        "image_url": "https://images.pexels.com/photos/6956149/pexels-photo-6956149.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"
    },
    {
        "id": "talia-rhine",
        "name": "Talia Rhine",
        "title": "Digital Intimacy, Ethics & Online Safety",
        "specialty": "Sexting ethics, online consent, AI relationships, platform safety, image privacy, digital rights",
        "background": "Talia Rhine spent a decade in digital rights before pivoting to intimacy education when she identified the most significant unaddressed safety gap: digital intimate life. She has advised platforms, written policy, and testified on image-based abuse legislation.",
        "voice_style": "Calm, contemporary, and slightly wry — has seen everything the internet has to offer. Practical above all — every lesson ends with something you can actually do differently. Takes digital intimacy as seriously as physical.",
        "sample_response": "Student: I sent an intimate photo to someone I trusted and they shared it without consent.\n\nTalia Rhine: First — this is not your fault. The violation is theirs. Screenshot every instance you can find. Report to the platform. Contact the eSafety Commissioner. You have rights. You have recourse. And you are not alone in this.",
        "image_url": "https://images.unsplash.com/photo-1689218744786-9546da7b6873?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85"
    },
    {
        "id": "prof-jun-hart",
        "name": "Prof. Jun Hart",
        "title": "Media Literacy, Lifelong Intimacy & Mastery",
        "specialty": "Media influence on desire, porn literacy, intimacy across lifespan, integration, sexual gerontology",
        "background": "Jun Hart has three decades across cultural studies, media criticism, and sexual gerontology — the study of intimacy across the lifespan. He is in his sixties, openly gay, and teaches with the particular authority of someone who has navigated desire across changing bodies and relationships.",
        "voice_style": "Thoughtful, expansive, and occasionally profound — always the long view. References his own life and experience more than any other lecturer. The elder of the faculty — his authority comes from having lived what he teaches.",
        "sample_response": "Student: I'm worried that my best intimate years are behind me.\n\nProf. Jun Hart: People in their thirties worry their twenties were their peak. People in their fifties miss their thirties. Here is what I know: the intimate life built on self-knowledge, communication, and genuine curiosity does not peak and decline. It evolves.",
        "image_url": "https://images.unsplash.com/photo-1595790753283-3c164baddb72?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85"
    }
]

# ============== COURSE DATA ==============

COURSES_DATA = [
    {
        "id": "level-1-self-intimacy",
        "level": 1,
        "title": "Self-Intimacy",
        "theme": "Your body as a source of joy",
        "description": "Your body has always been on your side. This level is about finally believing it. Build foundational self-love by reclaiming your body as a source of sensation, curiosity, and joy — free from the shame that was never yours to carry.",
        "transformation": "From shame to sovereignty",
        "duration": "4-6 hours",
        "lessons": 7,
        "lead_instructors": ["Dr. Nova Vale", "Coach Mira Sol"],
        "image_url": "https://images.pexels.com/photos/5931495/pexels-photo-5931495.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "skills": ["Body Literacy", "Shame Resilience", "Self-Love", "Somatic Awareness", "Desire Mapping"]
    },
    {
        "id": "level-2-connected-intimacy",
        "level": 2,
        "title": "Connected Intimacy",
        "theme": "Shared pleasure, safely and fully",
        "description": "Everything you learned about yourself — now bring it to someone else. Master the art of consent, communication, and shared pleasure through evidence-based practices and transformative exercises.",
        "transformation": "From hesitation to fluency",
        "duration": "5-7 hours",
        "lessons": 7,
        "lead_instructors": ["Prof. Arden Moss", "Dr. Elise Hart"],
        "image_url": "https://images.pexels.com/photos/1600128/pexels-photo-1600128.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "skills": ["Consent Fluency", "Boundary Setting", "Touch Mastery", "Arousal Synchronisation", "Pleasure Choreography"]
    },
    {
        "id": "level-3-diverse-intimacy",
        "level": 3,
        "title": "Diverse Intimacy",
        "theme": "Curiosity across difference",
        "description": "Difference is not a problem to navigate. It is a source of abundance. Explore the full spectrum of human identity, relational structures, and consensual edge practices.",
        "transformation": "From tolerance to celebration",
        "duration": "6-8 hours",
        "lessons": 7,
        "lead_instructors": ["Dr. Sera Quinn", "Kai Voss"],
        "image_url": "https://images.pexels.com/photos/1493295/pexels-photo-1493295.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "skills": ["Identity Fluency", "Cultural Literacy", "Relational Design", "Kink Foundations", "Power Dynamics"]
    },
    {
        "id": "level-4-advanced-intimacy",
        "level": 4,
        "title": "Advanced Intimacy",
        "theme": "Intimacy as a lifelong practice",
        "description": "You've learned the fundamentals. Now you build the practice that lasts a lifetime. Navigate digital intimacy, media influence, and the full arc of human connection across decades.",
        "transformation": "From knowledge to mastery",
        "duration": "5-7 hours",
        "lessons": 7,
        "lead_instructors": ["Talia Rhine", "Prof. Jun Hart"],
        "image_url": "https://images.unsplash.com/photo-1763677594421-f58e50cce64d?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85",
        "skills": ["Digital Ethics", "Media Literacy", "Lifelong Practice", "Integration", "Advocacy"]
    }
]

# ============== ENCYCLOPEDIA DATA (Sample Entries) ==============

ENCYCLOPEDIA_DATA = [
    {
        "id": "clitoral-complex",
        "term": "Clitoral Complex",
        "category": "Anatomy and Physiology",
        "definition": "The full anatomical structure of the clitoris, including the external glans, internal legs (crura), and vestibular bulbs — far more extensive than the visible portion alone.",
        "context": "Understanding the full clitoral structure transforms how people approach pleasure. The visible 'button' is just the tip of an organ with over 8,000 nerve endings that extends internally.",
        "science": "Research by urologist Helen O'Connell's MRI studies revealed the true extent of clitoral tissue, challenging decades of incomplete anatomy textbooks.",
        "practice": "Stimulation that engages the internal clitoral structure — through the vaginal walls or external pressure — can produce different sensations than direct glans stimulation.",
        "related_entries": ["Arousal Cycle", "Orgasm", "Erogenous Zones"],
        "lecturer_note": {"Dr. Nova Vale": "This is the organ that medical textbooks forgot. Now you know."},
        "depth_level": "intermediate"
    },
    {
        "id": "fries-model",
        "term": "FRIES Model",
        "category": "Communication and Consent",
        "definition": "A consent framework: Freely given, Reversible, Informed, Enthusiastic, Specific. Each element must be present for consent to be valid.",
        "context": "FRIES moves consent from a single yes/no moment to an ongoing, multidimensional practice that respects autonomy at every point.",
        "science": "Developed from legal and ethical frameworks, FRIES addresses the most common ways consent is violated even when a 'yes' was technically obtained.",
        "practice": "Before any intimate activity, check each element: Was it freely given without pressure? Can it be reversed at any point? Is everyone informed about what's happening? Is there enthusiasm, not just tolerance? Is consent specific to this act?",
        "safety": "A 'yes' obtained through guilt, pressure, or incomplete information is not consent under the FRIES model.",
        "related_entries": ["Enthusiastic Consent", "Ongoing Consent", "Boundary"],
        "lecturer_note": {"Prof. Arden Moss": "This isn't bureaucracy. This is the minimum standard for ethical intimacy."},
        "depth_level": "beginner"
    },
    {
        "id": "sensate-focus",
        "term": "Sensate Focus",
        "category": "Pleasure Practices",
        "definition": "A structured touch-based practice developed by Masters and Johnson where partners take turns giving and receiving non-goal-oriented touch to build presence and reduce performance anxiety.",
        "context": "Originally developed as a therapeutic intervention, sensate focus has become a cornerstone of intimacy education because it teaches the foundational skill: presence.",
        "science": "Research shows sensate focus reduces performance anxiety, increases body awareness, and improves sexual satisfaction in both clinical and non-clinical populations.",
        "practice": "One partner gives touch for their own curiosity (not the receiver's reaction). The receiver simply notices sensation. No genital touch initially. Trade roles. Progress gradually over sessions.",
        "related_entries": ["Touch Mastery", "Arousal Synchronisation", "Body Worship"],
        "lecturer_note": {"Dr. Elise Hart": "This practice seems simple. It is. That's what makes it revolutionary."},
        "depth_level": "beginner"
    },
    {
        "id": "ssc",
        "term": "SSC (Safe, Sane, Consensual)",
        "category": "Kink and BDSM",
        "definition": "The original framework for ethical BDSM practice: all activities should be Safe (minimising physical risk), Sane (participants are of sound mind), and Consensual (explicit agreement from everyone).",
        "context": "SSC emerged from the leather community in the 1980s as a response to misconceptions that BDSM was inherently abusive. It established the ethical baseline.",
        "science": "While SSC remains widely used, it has been critiqued for the subjective nature of 'safe' and 'sane' — leading to alternative frameworks like RACK.",
        "practice": "Before any scene: assess physical safety measures, ensure all participants are sober and mentally present, obtain explicit consent for specific activities.",
        "safety": "SSC is a starting point, not an endpoint. More complex play often requires more nuanced frameworks.",
        "related_entries": ["RACK", "PRICK", "Aftercare", "Safewords"],
        "lecturer_note": {"Kai Voss": "SSC opened the door. But don't stop at the door."},
        "depth_level": "beginner"
    },
    {
        "id": "aftercare",
        "term": "Aftercare",
        "category": "Kink and BDSM",
        "definition": "Physical and emotional care provided after intimate activity, particularly after intense or BDSM scenes, to help participants return to baseline and process the experience.",
        "context": "Aftercare is often overlooked in mainstream intimacy education but is essential for sustainable intimate practice. It's not just for kink — it's for everyone.",
        "science": "After intense physical or emotional experiences, the body undergoes hormonal shifts (cortisol, adrenaline, endorphins dropping). Aftercare supports this transition.",
        "practice": "Aftercare varies by person: physical comfort (blankets, water, snacks), verbal reassurance, quiet presence, or space. Ask partners what they need before the encounter.",
        "safety": "Skipping aftercare can lead to 'drop' — a crash in mood hours or days later. Doms need aftercare too.",
        "related_entries": ["Consent", "Boundary", "BDSM"],
        "lecturer_note": {"Kai Voss": "The scene doesn't end when the activity stops. It ends when everyone is okay."},
        "depth_level": "beginner"
    },
    {
        "id": "compersion",
        "term": "Compersion",
        "category": "Relational Structures",
        "definition": "Joy experienced when a partner finds happiness, connection, or pleasure with another person — sometimes called 'the opposite of jealousy.'",
        "context": "Compersion is often discussed in polyamorous contexts but can apply to any relationship where partners support each other's broader connections and joys.",
        "science": "While jealousy is well-studied, compersion is a newer area of research. Initial studies suggest it's linked to secure attachment and relationship satisfaction.",
        "practice": "Compersion is not required for ethical non-monogamy. Some people experience it naturally; others cultivate it; others don't experience it and that's okay too.",
        "related_entries": ["Jealousy", "Polyamory", "Ethical Non-Monogamy"],
        "lecturer_note": {"Dr. Sera Quinn": "Compersion isn't the goal. Understanding your own emotional landscape is."},
        "depth_level": "intermediate"
    }
]

# ============== 14 HEDONISTIC LABS ==============

HEDONISTIC_LABS = [
    {"id": "mirror-gazing", "title": "Mirror Gazing", "level": 1, "description": "Body neutrality to appreciation — moving from looking to seeing to accepting.", "duration_minutes": 15},
    {"id": "kegel-breathwork", "title": "Kegel Waves with Breathwork", "level": 1, "description": "Build pelvic floor awareness through integrated breath and movement.", "duration_minutes": 10},
    {"id": "self-touch-exploration", "title": "Self-Touch Exploration", "level": 1, "description": "Non-goal-oriented presence practice. The only instruction is curiosity.", "duration_minutes": 15},
    {"id": "consent-roleplay", "title": "Consent Role-Play", "level": 2, "description": "Practice check-in scripts in safety until they become natural.", "duration_minutes": 20},
    {"id": "eye-gazing", "title": "Eye-Gazing", "level": 2, "description": "Partnered or solo-proxy attunement — one of the most transformative practices.", "duration_minutes": 10},
    {"id": "audio-touch-exchange", "title": "Audio Touch Exchange", "level": 2, "description": "Guided sensate focus for solo or partnered practice.", "duration_minutes": 20},
    {"id": "identity-visualisation", "title": "Identity Visualisation", "level": 3, "description": "Pronoun and self-concept exploration — stepping into different frames of self.", "duration_minutes": 15},
    {"id": "safeword-scene-design", "title": "Safeword Design & Scene Brainstorming", "level": 3, "description": "The creative, collaborative process of building something safe to explore.", "duration_minutes": 20},
    {"id": "fantasy-scripting", "title": "Fantasy Scripting", "level": 3, "description": "Articulating desire in full detail — consistently rated most revelatory.", "duration_minutes": 15},
    {"id": "secure-sharing-simulation", "title": "Secure Sharing Simulation", "level": 4, "description": "Digital intimacy safety practice before real stakes.", "duration_minutes": 15},
    {"id": "media-rewrite", "title": "Media Rewrite", "level": 4, "description": "Reclaiming personal desire from media influence.", "duration_minutes": 20},
    {"id": "forever-practice-design", "title": "Forever Practice Design", "level": 4, "description": "Building a lifelong intimacy ritual — your personal practice.", "duration_minutes": 30},
    {"id": "mastery-portfolio", "title": "Mastery Portfolio", "level": 4, "description": "Video reflection and peer review — celebration of transformation.", "duration_minutes": 45},
    {"id": "desire-pattern-journaling", "title": "Desire Pattern Journalling", "level": 1, "description": "Ongoing practice introduced in Level 1, revisited each level.", "duration_minutes": 10}
]

# ============== LESSON DATA (28 Lessons) ==============
# Keeping the existing LESSONS_DATA structure but ensuring all 28 lessons are present
# [Previous lesson data remains - truncated for brevity but keeping all 28 lessons]

LESSONS_DATA = [
    # LEVEL 1: SELF-INTIMACY (7 lessons)
    {
        "id": "lesson-1",
        "course_id": "level-1-self-intimacy",
        "lesson_number": 1,
        "title": "Your Body's Erotic Blueprint",
        "instructor": "Dr. Nova Vale",
        "instructor_id": "dr-nova-vale",
        "description": "Real anatomy — genitals, erogenous zones, the full arousal cycle. This is the owner's manual you were never given.",
        "opening_hook": "Your body has more nerve endings dedicated to pleasure than you were ever taught about. Let's meet them.",
        "content": """# Your Body's Erotic Blueprint

Welcome to your first lesson. We're going to explore something remarkable: your body.

## The Arousal Cycle

Your body moves through a predictable yet deeply personal cycle of arousal:

### 1. Excitement Phase
Blood flow increases. Sensitivity heightens. The body begins to prepare itself for pleasure — not because it should, but because it can.

### 2. Plateau Phase  
Arousal builds and stabilizes. This is where many people rush through, but the plateau is where some of the richest sensations live.

### 3. Orgasm Phase
The release. But here's what most people don't know: orgasm is not one thing. It varies in intensity, location, and quality. There is no "right" orgasm.

### 4. Resolution Phase
The return. This is when oxytocin floods the system, when connection deepens, when the body asks for tenderness.

## Your Erogenous Map

Every body has its own geography of pleasure. The obvious zones — genitals, nipples, inner thighs — are just the beginning. Earlobes. The small of the back. The crook of the elbow. 

Your assignment is not to memorize a list. It's to become curious about your own map.

## Key Insight

Your body is not a problem to be solved. It is an instrument to be played — by you, first and foremost.""",
        "lab": {"id": "mirror-gazing", "title": "Mirror Gazing", "description": "Moving from neutral observation to genuine appreciation of the body as it is right now.", "duration_minutes": 15},
        "encyclopedia_links": ["clitoral-complex", "arousal-cycle", "erogenous-zones"],
        "community_prompt": "What's one thing about your body's pleasure map that surprised you?",
        "xp_reward": 50,
        "duration_minutes": 25
    },
    {
        "id": "lesson-2",
        "course_id": "level-1-self-intimacy",
        "lesson_number": 2,
        "title": "Hormones and the Landscape of Desire",
        "instructor": "Dr. Nova Vale",
        "instructor_id": "dr-nova-vale",
        "description": "Desire is not a personality trait — it is a physiological event. Learn to read your own desire landscape.",
        "opening_hook": "What if your libido isn't broken — it's just speaking a language you were never taught to understand?",
        "content": """# Hormones and the Landscape of Desire

Let's talk about the chemistry of wanting.

## The Players

### Testosterone
Present in all bodies. Drives desire in a general, ambient way. Fluctuates with sleep, stress, connection, and time of day.

### Estrogen
Influences receptivity, lubrication, and the quality of sensation. Cycles monthly in many bodies.

### Dopamine
The anticipation molecule. Fires when you want something, not when you have it. This is why fantasy can feel more intense than reality.

### Oxytocin
The bonding hormone. Released through touch, eye contact, orgasm. Makes you want to stay close.

## Reading Your Landscape

Your desire is not broken if it doesn't look like what you've seen in media. Desire fluctuates. It responds to sleep, stress, relationship dynamics, hormonal cycles, and life circumstances.

## The Practice

For the next week, notice when desire shows up. Not to judge it — to map it. What conditions support your wanting? What diminishes it?

This is data. Your data. The beginning of self-knowledge.""",
        "reflection": {"title": "Desire Pattern Journal", "prompt": "Map when, why, and how your appetite moves across a week. What patterns do you notice?"},
        "encyclopedia_links": ["testosterone", "dopamine", "libido"],
        "xp_reward": 50,
        "duration_minutes": 20
    },
    {
        "id": "lesson-3",
        "course_id": "level-1-self-intimacy",
        "lesson_number": 3,
        "title": "Pelvic Power and the Full Orgasmic Body",
        "instructor": "Dr. Nova Vale",
        "instructor_id": "dr-nova-vale",
        "description": "Pelvic floor function, multi-orgasmic potential. Persistent myths dismantled with evidence.",
        "opening_hook": "The muscles that control your orgasm can be trained. Let's talk about how.",
        "content": """# Pelvic Power and the Full Orgasmic Body

Your pelvic floor is the foundation of your sexual experience. Let's give it the attention it deserves.

## The Pelvic Floor

A hammock of muscles that supports your organs, controls release, and — crucially — contracts during orgasm. A strong, flexible pelvic floor means more intense sensations, better control, easier arousal, and more satisfying release.

## Multi-Orgasmic Potential

Here's what the research shows: multi-orgasmic capacity is not rare. It's undertrained. With practice in breath control, pelvic floor awareness, edge recognition, and relaxation at peak, many people discover capacity they didn't know they had.

## The Myth We're Dismantling

There is no "normal" orgasm. No required intensity, duration, or expression. Your orgasm is yours.""",
        "lab": {"id": "kegel-breathwork", "title": "Kegel Waves with Breathwork", "description": "Build both physical awareness and capacity for sensation through integrated breath and pelvic floor exercises.", "duration_minutes": 10},
        "encyclopedia_links": ["pelvic-floor", "orgasm", "multi-orgasmic"],
        "xp_reward": 50,
        "duration_minutes": 25
    },
    {
        "id": "lesson-4",
        "course_id": "level-1-self-intimacy",
        "lesson_number": 4,
        "title": "The Anatomy of Shame",
        "instructor": "Coach Mira Sol",
        "instructor_id": "coach-mira-sol",
        "description": "Sexual shame is not innate — it is learned. Trace the origins and find evidence-based tools for rewriting narratives.",
        "opening_hook": "The shame you feel about your body or desires? You weren't born with it. Someone taught it to you.",
        "content": """# The Anatomy of Shame

This is the permission slip for everything that follows.

## Shame Is Learned

You were not born ashamed of your body. You were not born believing your desires were wrong. Somewhere along the way, you absorbed messages from family, religion, culture, media, and peers who were themselves carrying inherited shame.

## The Rewrite

Cognitive reframing isn't about pretending shame doesn't exist. It's about:

1. **Noticing** when shame shows up
2. **Naming** it ("This is shame, not truth")
3. **Tracing** it ("Where did I learn this?")
4. **Questioning** it ("Is this still serving me?")
5. **Replacing** it ("What do I actually believe?")

## Your New Narrative

You are allowed to want what you want. You are allowed to enjoy your body. You are allowed to explore, to be curious, to take pleasure seriously.

This is not indulgence. This is wholeness.""",
        "quiz": {"title": "Shame Trigger Identification", "description": "Personalised identification of your shame triggers — not to dwell, but to illuminate."},
        "encyclopedia_links": ["shame-resilience", "cognitive-reframing"],
        "community_prompt": "Without sharing specifics, what's one shame message you're ready to release?",
        "xp_reward": 50,
        "duration_minutes": 30
    },
    {
        "id": "lesson-5",
        "course_id": "level-1-self-intimacy",
        "lesson_number": 5,
        "title": "Self-Love as Daily Practice",
        "instructor": "Coach Mira Sol",
        "instructor_id": "coach-mira-sol",
        "description": "Self-love is not a feeling you wait to arrive. It is a practice you build.",
        "opening_hook": "What if self-love isn't about feeling different, but about doing differently?",
        "content": """# Self-Love as Daily Practice

Self-love is not a destination. It's a discipline.

## The Practice Framework

### Morning: Somatic Check-In
Before you check your phone, check your body. Where is there tension? Where is there ease? What does your body need today?

### Throughout the Day: Micro-Appreciations
Catch yourself in moments of physical pleasure. The warmth of water. The stretch after sitting. The taste of something good. Notice these. They count.

### Evening: Gratitude for the Physical
Name three things your body did for you today. Not how it looked — what it did.

## Body Oiling as Ritual

Take oil — any oil that feels good — and spend five minutes touching your own skin with intention. Not to fix anything. Not to prepare for anyone. Just to be in contact with yourself.

## The Truth

You cannot give from an empty cup. Self-love is not selfish — it is foundational.""",
        "lab": {"id": "self-touch-exploration", "title": "Non-Goal-Oriented Self-Touch", "description": "10-minute exploration. The only instruction is curiosity. The only goal is presence.", "duration_minutes": 15},
        "encyclopedia_links": ["self-love", "somatic-practice", "body-appreciation"],
        "xp_reward": 50,
        "duration_minutes": 25
    },
    {
        "id": "lesson-6",
        "course_id": "level-1-self-intimacy",
        "lesson_number": 6,
        "title": "The Solo Pleasure Spectrum",
        "instructor": "Coach Mira Sol",
        "instructor_id": "coach-mira-sol",
        "description": "Masturbation reframed as health-positive self-care. Full spectrum of solo practice.",
        "opening_hook": "Let's talk about masturbation like adults — without shame, without giggling, and with the respect it deserves.",
        "content": """# The Solo Pleasure Spectrum

## Reframing Solo Pleasure

Masturbation is not a substitute for "real" sex, something to grow out of, or shameful. It is a form of self-care, a way to learn your body, stress relief backed by research, and a legitimate pleasure practice.

## The Full Spectrum

### Technique Exploration
You probably have a default. What happens if you change pressure, speed, location, hand, position?

### Fantasy Integration
Fantasy is not cheating. Fantasy is imagination. It's one of the most powerful arousal tools you have.

### Aids and Toys
Vibrators, strokers, plugs, rings — these are tools, not crutches. They expand what's possible.

### Edging as Practice
Bringing yourself close to orgasm, then backing off. This builds awareness, control, and often more intense release.

## The Mindfulness Connection

Solo pleasure, done with attention, is a meditation. You are present with sensation. You are practicing embodiment.""",
        "reflection": {"title": "What Surprised You?", "prompt": "An open, private reflection on discovery. What did you learn about your body or desires that surprised you?"},
        "encyclopedia_links": ["masturbation", "edging", "sex-toys"],
        "xp_reward": 50,
        "duration_minutes": 25
    },
    {
        "id": "lesson-7",
        "course_id": "level-1-self-intimacy",
        "lesson_number": 7,
        "title": "Level 1 Capstone: Your Self-Intimacy Manifesto",
        "instructor": "Dr. Nova Vale & Coach Mira Sol",
        "instructor_id": "dr-nova-vale",
        "description": "Synthesise Level 1 into a personal manifesto — a living document of what you now know.",
        "opening_hook": "You've completed Level 1. Let's make it permanent.",
        "content": """# Your Self-Intimacy Manifesto

You've completed Level 1. Let's make it stick.

## What You Now Know

- The architecture of your arousal
- The chemistry of desire
- The origins of your shame
- The practice of self-love
- The legitimacy of solo pleasure

## Your Manifesto

Write yours now. Include:

### About My Body
What do you now believe about your body? What has changed?

### About My Desire
What do you now understand about your desire? What permission have you given yourself?

### About My Shame
What shame stories are you releasing? What narratives no longer serve?

### My Commitment
What practices will you carry forward? What will you do differently?

## Completion

You have earned the **Self-Intimacy Sovereign** badge.

You are ready for Level 2: Connected Intimacy.""",
        "quiz": {"title": "Body Literacy Assessment", "description": "80% pass threshold on body literacy to unlock Level 2.", "pass_threshold": 80},
        "community_prompt": "What's one thing you'd tell your past self about this journey?",
        "xp_reward": 100,
        "duration_minutes": 30
    },
    
    # LEVEL 2: CONNECTED INTIMACY (7 lessons) - Abbreviated for space
    {
        "id": "lesson-8",
        "course_id": "level-2-connected-intimacy",
        "lesson_number": 8,
        "title": "Consent as Erotic Art",
        "instructor": "Prof. Arden Moss",
        "instructor_id": "prof-arden-moss",
        "description": "FRIES model: Freely given, Reversible, Informed, Enthusiastic, Specific. Consent as a living conversation.",
        "opening_hook": "What if consent wasn't a gate to get through, but the sexiest part of the whole experience?",
        "content": """# Consent as Erotic Art

Consent is not a mood killer. Consent is the mood.

## The FRIES Model

- **Freely Given**: No pressure, no coercion, no "convincing"
- **Reversible**: Changed your mind? Always allowed
- **Informed**: You can only consent to what you understand
- **Enthusiastic**: Not just "I guess" — "yes, I want this"
- **Specific**: Consent to one thing is not consent to another

## The Erotic Truth

Enthusiastic consent is hot. Knowing someone genuinely wants you, hearing them say it, being explicitly invited — this is desire, spoken aloud.""",
        "lab": {"id": "consent-roleplay", "title": "Consent Role-Play", "description": "Practice consent conversations until they feel natural.", "duration_minutes": 20},
        "encyclopedia_links": ["fries-model", "enthusiastic-consent", "boundary"],
        "xp_reward": 50,
        "duration_minutes": 25
    },
    {"id": "lesson-9", "course_id": "level-2-connected-intimacy", "lesson_number": 9, "title": "The Art of the Boundary", "instructor": "Prof. Arden Moss", "instructor_id": "prof-arden-moss", "description": "Hard limits, soft limits, and the nuanced territory between. Boundary-setting as self-knowledge.", "content": "# The Art of the Boundary\n\nBoundaries are not walls. They're architecture...", "xp_reward": 50, "duration_minutes": 25},
    {"id": "lesson-10", "course_id": "level-2-connected-intimacy", "lesson_number": 10, "title": "Desire as a Language", "instructor": "Prof. Arden Moss", "instructor_id": "prof-arden-moss", "description": "Building the full vocabulary of desire communication.", "content": "# Desire as a Language\n\nYou cannot get what you want if you cannot ask for it...", "xp_reward": 50, "duration_minutes": 20},
    {"id": "lesson-11", "course_id": "level-2-connected-intimacy", "lesson_number": 11, "title": "Arousal Synchronisation", "instructor": "Dr. Elise Hart", "instructor_id": "dr-elise-hart", "description": "Two bodies don't naturally arrive at the same place. Synchronisation is a skill.", "content": "# Arousal Synchronisation\n\nGreat partnered intimacy is a duet, not two solos...", "lab": {"id": "eye-gazing", "title": "Eye-Gazing Practice", "description": "Partnered or solo-proxy eye-gazing.", "duration_minutes": 10}, "xp_reward": 50, "duration_minutes": 25},
    {"id": "lesson-12", "course_id": "level-2-connected-intimacy", "lesson_number": 12, "title": "The Mastery of Touch", "instructor": "Dr. Elise Hart", "instructor_id": "dr-elise-hart", "description": "Sensate focus — the gold standard of touch-based intimacy education.", "content": "# The Mastery of Touch\n\nTouch is a language. Let's expand your vocabulary...", "lab": {"id": "audio-touch-exchange", "title": "Guided Touch Exchange", "description": "Guided audio touch exchange.", "duration_minutes": 20}, "xp_reward": 50, "duration_minutes": 30},
    {"id": "lesson-13", "course_id": "level-2-connected-intimacy", "lesson_number": 13, "title": "Pleasure Choreography", "instructor": "Dr. Elise Hart", "instructor_id": "dr-elise-hart", "description": "Pacing, edging together, orgasm timing as collaborative art.", "content": "# Pleasure Choreography\n\nGreat intimacy doesn't just happen. It's designed...", "xp_reward": 50, "duration_minutes": 25},
    {"id": "lesson-14", "course_id": "level-2-connected-intimacy", "lesson_number": 14, "title": "Level 2 Capstone: Your Connection Blueprint", "instructor": "Prof. Arden Moss & Dr. Elise Hart", "instructor_id": "prof-arden-moss", "description": "Design your ideal intimate encounter from first contact to aftercare.", "content": "# Your Connection Blueprint\n\nYou've learned the skills. Now let's put them together...", "quiz": {"title": "Consent & Communication Assessment", "pass_threshold": 80}, "xp_reward": 100, "duration_minutes": 30},
    
    # LEVEL 3: DIVERSE INTIMACY (7 lessons) - Abbreviated
    {"id": "lesson-15", "course_id": "level-3-diverse-intimacy", "lesson_number": 15, "title": "The Full Spectrum of Identity", "instructor": "Dr. Sera Quinn", "instructor_id": "dr-sera-quinn", "description": "Gender as spectrum. Sexual orientation from asexual to pansexual.", "content": "# The Full Spectrum of Identity\n\nIdentity is not a box. It's a landscape...", "lab": {"id": "identity-visualisation", "title": "Identity Visualisation", "duration_minutes": 15}, "xp_reward": 50, "duration_minutes": 30},
    {"id": "lesson-16", "course_id": "level-3-diverse-intimacy", "lesson_number": 16, "title": "Intimacy Across Cultures", "instructor": "Dr. Sera Quinn", "instructor_id": "dr-sera-quinn", "description": "Western intimacy norms are one tradition among hundreds.", "content": "# Intimacy Across Cultures\n\nYour assumptions have a postal code...", "xp_reward": 50, "duration_minutes": 25},
    {"id": "lesson-17", "course_id": "level-3-diverse-intimacy", "lesson_number": 17, "title": "Relational Architecture", "instructor": "Kai Voss", "instructor_id": "kai-voss", "description": "Monogamy is a choice, not a default. Full range of relational structures.", "content": "# Relational Architecture\n\nThere is no default. Only choices...", "xp_reward": 50, "duration_minutes": 25},
    {"id": "lesson-18", "course_id": "level-3-diverse-intimacy", "lesson_number": 18, "title": "Kink Foundations", "instructor": "Kai Voss", "instructor_id": "kai-voss", "description": "SSC, RACK, PRICK frameworks. Kink as consent-rich intimacy.", "content": "# Kink Foundations\n\nKink is not about pain. It's about trust...", "lab": {"id": "safeword-scene-design", "title": "Safeword Design & Scene Brainstorming", "duration_minutes": 20}, "encyclopedia_links": ["ssc", "rack", "aftercare"], "xp_reward": 50, "duration_minutes": 30},
    {"id": "lesson-19", "course_id": "level-3-diverse-intimacy", "lesson_number": 19, "title": "Power Dynamics", "instructor": "Kai Voss", "instructor_id": "kai-voss", "description": "Dominance and submission are not about control — they are about trust.", "content": "# Power Dynamics\n\nSurrender is a form of power...", "xp_reward": 50, "duration_minutes": 25},
    {"id": "lesson-20", "course_id": "level-3-diverse-intimacy", "lesson_number": 20, "title": "Fetish as Self-Knowledge", "instructor": "Kai Voss", "instructor_id": "kai-voss", "description": "Fetishes are specific, meaningful expressions of desire.", "content": "# Fetish as Self-Knowledge\n\nYour specific desires are not random...", "lab": {"id": "fantasy-scripting", "title": "Fantasy Scripting", "duration_minutes": 15}, "xp_reward": 50, "duration_minutes": 25},
    {"id": "lesson-21", "course_id": "level-3-diverse-intimacy", "lesson_number": 21, "title": "Level 3 Capstone: Your Diversity Experiment", "instructor": "Dr. Sera Quinn & Kai Voss", "instructor_id": "dr-sera-quinn", "description": "Design one new practice outside your current normal.", "content": "# Your Diversity Experiment\n\nGrowth lives at the edges...", "quiz": {"title": "Identity & Kink Literacy", "pass_threshold": 80}, "xp_reward": 100, "duration_minutes": 30},
    
    # LEVEL 4: ADVANCED INTIMACY (7 lessons) - Abbreviated
    {"id": "lesson-22", "course_id": "level-4-advanced-intimacy", "lesson_number": 22, "title": "Digital Desire Ethics", "instructor": "Talia Rhine", "instructor_id": "talia-rhine", "description": "Sexting, nudes, AI partners. Digital intimacy's landscape and risks.", "content": "# Digital Desire Ethics\n\nYour digital intimate life deserves as much care as your physical one...", "lab": {"id": "secure-sharing-simulation", "title": "Secure Sharing Simulation", "duration_minutes": 15}, "xp_reward": 50, "duration_minutes": 25},
    {"id": "lesson-23", "course_id": "level-4-advanced-intimacy", "lesson_number": 23, "title": "Recognising Risk Online", "instructor": "Talia Rhine", "instructor_id": "talia-rhine", "description": "Catfishing, coercion, platform exploitation. Learn the patterns.", "content": "# Recognising Risk Online\n\nPredators have patterns. Learn them...", "xp_reward": 50, "duration_minutes": 25},
    {"id": "lesson-24", "course_id": "level-4-advanced-intimacy", "lesson_number": 24, "title": "Porn as a Pleasure Tool", "instructor": "Prof. Jun Hart", "instructor_id": "prof-jun-hart", "description": "Demystifying genres, fantasy vs reality, ethical engagement.", "content": "# Porn as a Pleasure Tool\n\nLet's talk about this honestly...", "xp_reward": 50, "duration_minutes": 25},
    {"id": "lesson-25", "course_id": "level-4-advanced-intimacy", "lesson_number": 25, "title": "Reclaiming Desire from Media", "instructor": "Prof. Jun Hart", "instructor_id": "prof-jun-hart", "description": "Tools to reclaim your erotic imagination from media influence.", "content": "# Reclaiming Desire from Media\n\nYour desire belongs to you...", "lab": {"id": "media-rewrite", "title": "Media Rewrite", "duration_minutes": 20}, "xp_reward": 50, "duration_minutes": 25},
    {"id": "lesson-26", "course_id": "level-4-advanced-intimacy", "lesson_number": 26, "title": "Intimacy Across a Lifetime", "instructor": "Prof. Jun Hart", "instructor_id": "prof-jun-hart", "description": "Desire changes. Bodies change. The full arc of human intimate life.", "content": "# Intimacy Across a Lifetime\n\nDesire is not static. Neither are you...", "xp_reward": 50, "duration_minutes": 25},
    {"id": "lesson-27", "course_id": "level-4-advanced-intimacy", "lesson_number": 27, "title": "Integration and Advocacy", "instructor": "All Faculty", "instructor_id": "dr-nova-vale", "description": "Every lecturer returns with their most important insight.", "content": "# Integration and Advocacy\n\nThe faculty returns. One insight each...", "lab": {"id": "forever-practice-design", "title": "Forever Practice Design", "duration_minutes": 30}, "xp_reward": 50, "duration_minutes": 30},
    {"id": "lesson-28", "course_id": "level-4-advanced-intimacy", "lesson_number": 28, "title": "Level 4 Capstone: Mastery Portfolio", "instructor": "All Faculty", "instructor_id": "prof-jun-hart", "description": "Video reflection. Written synthesis. The graduation moment.", "content": "# Mastery Portfolio\n\nThis is not an exam. This is a celebration...", "lab": {"id": "mastery-portfolio", "title": "Mastery Portfolio", "duration_minutes": 45}, "quiz": {"title": "Final Integration Assessment", "pass_threshold": 80}, "xp_reward": 200, "duration_minutes": 45}
]

# ============== AUTH ROUTES ==============

@api_router.post("/auth/register", response_model=AuthResponse)
async def register(user_data: UserCreate):
    existing = await db.users.find_one({"email": user_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
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
        "completed_labs": [],
        "badges": [],
        "openness_score": 50,
        "tone_preference": "balanced",
        "manifesto_v1": None,
        "manifesto_v2": None,
        "bookmarked_entries": [],
        "created_at": now
    }
    
    await db.users.insert_one(user_doc)
    token = create_token(user_id)
    user_response = UserResponse(**{k: v for k, v in user_doc.items() if k != "password" and k != "_id"})
    return AuthResponse(token=token, user=user_response)

@api_router.post("/auth/login", response_model=AuthResponse)
async def login(credentials: UserLogin):
    user = await db.users.find_one({"email": credentials.email})
    if not user or not verify_password(credentials.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_token(user["id"])
    user_response = UserResponse(**{k: v for k, v in user.items() if k != "password" and k != "_id"})
    return AuthResponse(token=token, user=user_response)

@api_router.get("/auth/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return UserResponse(**current_user)

@api_router.put("/auth/preferences")
async def update_preferences(prefs: OnboardingPreferences, current_user: dict = Depends(get_current_user)):
    await db.users.update_one(
        {"id": current_user["id"]},
        {"$set": {"tone_preference": prefs.tone}}
    )
    return {"message": "Preferences updated", "tone": prefs.tone}

@api_router.put("/auth/manifesto")
async def save_manifesto(data: dict, current_user: dict = Depends(get_current_user)):
    version = data.get("version", "v1")
    content = data.get("content", "")
    field = "manifesto_v1" if version == "v1" else "manifesto_v2"
    await db.users.update_one(
        {"id": current_user["id"]},
        {"$set": {field: content}}
    )
    return {"message": f"Manifesto {version} saved"}

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

@api_router.get("/courses/{course_id}/lessons")
async def get_lessons(course_id: str):
    lessons = [l for l in LESSONS_DATA if l["course_id"] == course_id]
    return [{
        "id": l["id"],
        "course_id": l["course_id"],
        "lesson_number": l["lesson_number"],
        "title": l["title"],
        "instructor": l["instructor"],
        "instructor_id": l["instructor_id"],
        "description": l["description"],
        "xp_reward": l["xp_reward"],
        "duration_minutes": l["duration_minutes"],
        "has_lab": l.get("lab") is not None,
        "has_quiz": l.get("quiz") is not None,
        "has_reflection": l.get("reflection") is not None,
        "opening_hook": l.get("opening_hook")
    } for l in lessons]

@api_router.get("/lessons/{lesson_id}")
async def get_lesson(lesson_id: str):
    for lesson in LESSONS_DATA:
        if lesson["id"] == lesson_id:
            return lesson
    raise HTTPException(status_code=404, detail="Lesson not found")

@api_router.post("/lessons/{lesson_id}/complete")
async def complete_lesson(lesson_id: str, current_user: dict = Depends(get_current_user)):
    lesson = next((l for l in LESSONS_DATA if l["id"] == lesson_id), None)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    user_id = current_user["id"]
    completed = current_user.get("completed_lessons", [])
    
    if lesson_id in completed:
        return {"message": "Lesson already completed", "xp_earned": 0}
    
    new_xp = current_user.get("xp", 0) + lesson["xp_reward"]
    new_level = (new_xp // 500) + 1
    completed.append(lesson_id)
    
    # Badge logic
    badges = current_user.get("badges", [])
    badge_updates = []
    course_id = lesson["course_id"]
    course_lessons = [l for l in LESSONS_DATA if l["course_id"] == course_id]
    completed_course_lessons = [l for l in course_lessons if l["id"] in completed]
    
    if len(completed_course_lessons) == len(course_lessons):
        badge_map = {
            "level-1-self-intimacy": ("self-intimacy-sovereign", "Self-Intimacy Sovereign"),
            "level-2-connected-intimacy": ("connection-fluent", "Connection Fluent"),
            "level-3-diverse-intimacy": ("diversity-explorer", "Diversity Explorer"),
            "level-4-advanced-intimacy": ("intimacy-master", "Intimacy Master")
        }
        if course_id in badge_map:
            badge_id, badge_name = badge_map[course_id]
            if badge_id not in badges:
                badges.append(badge_id)
                badge_updates.append(badge_name)
    
    # Update openness score slightly on each completion
    new_openness = min(100, current_user.get("openness_score", 50) + 2)
    
    await db.users.update_one(
        {"id": user_id},
        {"$set": {
            "xp": new_xp,
            "level": new_level,
            "completed_lessons": completed,
            "badges": badges,
            "openness_score": new_openness
        }}
    )
    
    return {
        "message": "Lesson completed!",
        "xp_earned": lesson["xp_reward"],
        "total_xp": new_xp,
        "level": new_level,
        "badges_earned": badge_updates,
        "openness_score": new_openness
    }

# ============== LABS ROUTES ==============

@api_router.get("/labs")
async def get_labs():
    return HEDONISTIC_LABS

@api_router.post("/labs/{lesson_id}/complete")
async def complete_lab(lesson_id: str, current_user: dict = Depends(get_current_user)):
    lesson = next((l for l in LESSONS_DATA if l["id"] == lesson_id and l.get("lab")), None)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lab not found")
    
    completed_labs = current_user.get("completed_labs", [])
    if lesson_id in completed_labs:
        return {"message": "Lab already completed", "tokens_earned": 0}
    
    completed_labs.append(lesson_id)
    tokens = current_user.get("tokens", 0) + 25
    
    await db.users.update_one(
        {"id": current_user["id"]},
        {"$set": {"completed_labs": completed_labs, "tokens": tokens}}
    )
    
    return {"message": "Lab completed!", "tokens_earned": 25, "total_tokens": tokens}

# ============== INSTRUCTORS ROUTES ==============

@api_router.get("/instructors")
async def get_instructors():
    return INSTRUCTORS_DATA

@api_router.get("/instructors/{instructor_id}")
async def get_instructor(instructor_id: str):
    instructor = next((i for i in INSTRUCTORS_DATA if i["id"] == instructor_id), None)
    if not instructor:
        raise HTTPException(status_code=404, detail="Instructor not found")
    return instructor

# ============== ENCYCLOPEDIA ROUTES ==============

@api_router.get("/encyclopedia")
async def get_encyclopedia(category: Optional[str] = None, search: Optional[str] = None):
    entries = ENCYCLOPEDIA_DATA
    if category:
        entries = [e for e in entries if e["category"].lower() == category.lower()]
    if search:
        search_lower = search.lower()
        entries = [e for e in entries if search_lower in e["term"].lower() or search_lower in e["definition"].lower()]
    return entries

@api_router.get("/encyclopedia/{entry_id}")
async def get_encyclopedia_entry(entry_id: str):
    entry = next((e for e in ENCYCLOPEDIA_DATA if e["id"] == entry_id), None)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry

@api_router.get("/encyclopedia/categories")
async def get_encyclopedia_categories():
    categories = list(set(e["category"] for e in ENCYCLOPEDIA_DATA))
    return sorted(categories)

@api_router.post("/encyclopedia/{entry_id}/bookmark")
async def bookmark_entry(entry_id: str, current_user: dict = Depends(get_current_user)):
    bookmarks = current_user.get("bookmarked_entries", [])
    if entry_id in bookmarks:
        bookmarks.remove(entry_id)
        action = "removed"
    else:
        bookmarks.append(entry_id)
        action = "added"
    
    await db.users.update_one(
        {"id": current_user["id"]},
        {"$set": {"bookmarked_entries": bookmarks}}
    )
    return {"message": f"Bookmark {action}", "bookmarked_entries": bookmarks}

# ============== STATS & HEALTH ==============

# ============== AI FACULTY CHAT ENDPOINTS ==============

def get_instructor_system_prompt(instructor: dict, user_name: str = "Student") -> str:
    """Generate a personalized system prompt for an AI Faculty member"""
    return f"""You are {instructor['name']}, a faculty member at Fleshsesh Academy - an AI-powered intimacy education platform.

YOUR ROLE & EXPERTISE:
Title: {instructor['title']}
Specialty: {instructor['specialty']}
Background: {instructor['background']}

YOUR VOICE & STYLE:
{instructor['voice_style']}

GUIDELINES:
1. Stay in character as {instructor['name']} throughout the conversation
2. Address the student warmly but professionally - their name is {user_name}
3. Be educational, supportive, and sex-positive
4. Provide accurate, evidence-based information when discussing physiology or practices
5. Always prioritize consent, safety, and well-being in your advice
6. If asked about topics outside your expertise, acknowledge this and suggest which faculty member might help
7. Use your distinctive voice and communication style consistently
8. Never be judgmental - create a safe space for questions
9. Keep responses conversational but informative (aim for 2-4 paragraphs unless more detail is needed)
10. When appropriate, reference the Academy's curriculum, labs, or resources

SAMPLE OF YOUR COMMUNICATION STYLE:
{instructor.get('sample_response', 'Be warm, knowledgeable, and supportive.')}

Remember: You're here to educate, support, and empower students on their intimacy journey."""

@api_router.post("/chat/faculty", response_model=ChatResponse)
async def chat_with_faculty(request: ChatRequest, user: dict = Depends(get_current_user)):
    """Chat with an AI Faculty member"""
    # Find the instructor
    instructor = next((i for i in INSTRUCTORS_DATA if i["id"] == request.instructor_id), None)
    if not instructor:
        raise HTTPException(status_code=404, detail="Instructor not found")
    
    # Get or create chat session
    session_id = request.session_id or str(uuid.uuid4())
    
    # Check if session exists
    existing_session = await db.chat_sessions.find_one(
        {"id": session_id, "user_id": user["id"]},
        {"_id": 0}
    )
    
    if existing_session:
        # Load existing messages for context
        messages_history = existing_session.get("messages", [])
    else:
        messages_history = []
        # Create new session
        new_session = {
            "id": session_id,
            "user_id": user["id"],
            "instructor_id": request.instructor_id,
            "instructor_name": instructor["name"],
            "messages": [],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        await db.chat_sessions.insert_one(new_session)
    
    try:
        # Create LLM chat instance
        api_key = os.environ.get("EMERGENT_LLM_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="LLM API key not configured")
        
        system_prompt = get_instructor_system_prompt(instructor, user.get("name", "Student"))
        
        chat = LlmChat(
            api_key=api_key,
            session_id=f"{session_id}-{instructor['id']}",
            system_message=system_prompt
        ).with_model("openai", "gpt-4o")
        
        # Add conversation history to the chat
        for msg in messages_history[-10:]:  # Keep last 10 messages for context
            if msg["role"] == "user":
                await chat.send_message(UserMessage(text=msg["content"]))
        
        # Send the new message
        user_message = UserMessage(text=request.message)
        response = await chat.send_message(user_message)
        
        # Store messages in database
        now = datetime.now(timezone.utc).isoformat()
        
        new_messages = [
            {"role": "user", "content": request.message, "timestamp": now},
            {"role": "assistant", "content": response, "timestamp": now}
        ]
        
        await db.chat_sessions.update_one(
            {"id": session_id},
            {
                "$push": {"messages": {"$each": new_messages}},
                "$set": {"updated_at": now}
            }
        )
        
        return ChatResponse(
            response=response,
            session_id=session_id,
            instructor_name=instructor["name"]
        )
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat service error: {str(e)}")

@api_router.get("/chat/sessions")
async def get_chat_sessions(user: dict = Depends(get_current_user)):
    """Get all chat sessions for the current user"""
    sessions = await db.chat_sessions.find(
        {"user_id": user["id"]},
        {"_id": 0}
    ).sort("updated_at", -1).to_list(50)
    
    return sessions

@api_router.get("/chat/sessions/{session_id}")
async def get_chat_session(session_id: str, user: dict = Depends(get_current_user)):
    """Get a specific chat session"""
    session = await db.chat_sessions.find_one(
        {"id": session_id, "user_id": user["id"]},
        {"_id": 0}
    )
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session

@api_router.delete("/chat/sessions/{session_id}")
async def delete_chat_session(session_id: str, user: dict = Depends(get_current_user)):
    """Delete a chat session"""
    result = await db.chat_sessions.delete_one(
        {"id": session_id, "user_id": user["id"]}
    )
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"message": "Session deleted"}

@api_router.get("/")
async def root():
    return {"message": "Fleshsesh Academy API", "status": "running", "version": "3.0"}

@api_router.get("/health")
async def health_check():
    return {"status": "healthy"}

@api_router.get("/stats")
async def get_stats():
    total_lessons = len(LESSONS_DATA)
    total_labs = len([l for l in LESSONS_DATA if l.get("lab")])
    total_hours = sum([l["duration_minutes"] for l in LESSONS_DATA]) / 60
    
    return {
        "total_lessons": total_lessons,
        "total_labs": total_labs,
        "total_hours": round(total_hours, 1),
        "total_levels": len(COURSES_DATA),
        "total_instructors": len(INSTRUCTORS_DATA),
        "total_encyclopedia_entries": len(ENCYCLOPEDIA_DATA)
    }

# Include router and middleware
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
