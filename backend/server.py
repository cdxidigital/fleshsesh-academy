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
    completed_labs: List[str] = []
    badges: List[str] = []
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
    lab: Optional[Dict[str, Any]] = None
    quiz: Optional[Dict[str, Any]] = None
    reflection: Optional[Dict[str, Any]] = None
    xp_reward: int = 50
    duration_minutes: int = 20

class Instructor(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    name: str
    title: str
    specialty: str
    description: str
    personality: Optional[str] = None
    teaching_style: Optional[str] = None
    tone: str
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

# ============== AI FACULTY DATA ==============

INSTRUCTORS_DATA = [
    {
        "id": "dr-nova-vale",
        "name": "Dr. Nova Vale",
        "title": "Sexual Physiology & Body Science",
        "specialty": "Anatomy, arousal physiology, hormonal cycles, orgasm science, pelvic health",
        "description": "The scientist of the group — but a scientist who understands that data without warmth is useless in a room this intimate. She teaches the body as a system of extraordinary intelligence.",
        "personality": "Combines rigorous scientific knowledge with genuine warmth. Makes complex anatomy accessible and fascinating. Celebrates the body's wisdom.",
        "teaching_style": "Uses interactive body maps, clear explanations of physiological processes, and evidence-based approaches. Dismantles myths with precision while maintaining compassion.",
        "tone": "Warm, authoritative, quietly thrilling",
        "image_url": "https://images.pexels.com/photos/5631041/pexels-photo-5631041.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"
    },
    {
        "id": "coach-mira-sol",
        "name": "Coach Mira Sol",
        "title": "Self-Love, Shame Resilience & Somatic Practice",
        "specialty": "Psychology, coaching, body-based healing, shame resilience, self-love practices",
        "description": "Works at the intersection of psychology, coaching, and body-based healing. Sits with the parts of you that were told you were too much, not enough, wrong for wanting what you want — and gently, firmly, dismantles every one of those messages.",
        "personality": "Creates a container of unconditional acceptance. Sees through protective layers to the authentic self underneath. Fierce advocate for self-compassion.",
        "teaching_style": "Combines cognitive reframing with somatic practices. Uses guided exercises, affirmations grounded in physical sensation, and gentle challenges to limiting beliefs.",
        "tone": "Tender, direct, occasionally fierce",
        "image_url": "https://images.unsplash.com/photo-1763906803356-c4c2c83dc012?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85"
    },
    {
        "id": "prof-arden-moss",
        "name": "Prof. Arden Moss",
        "title": "Consent, Communication & Relational Ethics",
        "specialty": "Consent frameworks, communication skills, boundary setting, relational ethics",
        "description": "Makes the case that consent is not a legal formality — it is an erotic skill, a relational art form, and the foundation of every genuinely pleasurable encounter. Teaches consent not as a checklist but as a living conversation.",
        "personality": "Intellectually brilliant yet deeply accessible. Finds the humanity in ethical frameworks. Makes difficult conversations feel possible.",
        "teaching_style": "Role-play scenarios, script practice, real-world application exercises. Builds skills through repetition until they become natural.",
        "tone": "Intellectually rigorous, deeply human, occasionally playful",
        "image_url": "https://images.unsplash.com/photo-1619241805829-34fb64299391?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85"
    },
    {
        "id": "dr-elise-hart",
        "name": "Dr. Elise Hart",
        "title": "Shared Pleasure & Partnered Practice",
        "specialty": "Sensate focus, attachment theory, practical pleasure education, touch mastery",
        "description": "Brings together sensate focus research, attachment theory, and practical pleasure education. Particularly skilled at teaching students how to be present — how to slow down, tune in, and find the extraordinary in the ordinary moment of connection.",
        "personality": "Radiates calm presence. Makes slowing down feel like an invitation rather than a demand. Expert at holding space for vulnerability.",
        "teaching_style": "Guided audio experiences, partnered practices, sensate focus techniques. Emphasizes presence and attunement over performance.",
        "tone": "Calm, expert, warmly sensual",
        "image_url": "https://images.pexels.com/photos/1493295/pexels-photo-1493295.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"
    },
    {
        "id": "dr-sera-quinn",
        "name": "Dr. Sera Quinn",
        "title": "Identity, Diversity & Intersectional Intimacy",
        "specialty": "Gender spectrum, sexual orientation, disability, neurodiversity, cultural frameworks",
        "description": "Teaches identity not as a box to tick but as a living, evolving dimension of who a person is. Shows students how understanding the full spectrum of human identity makes them more curious, more tolerant, and more capable of genuine connection across difference.",
        "personality": "Combines scholarly depth with personal warmth. Celebrates difference as abundance. Creates space for all identities to be seen and affirmed.",
        "teaching_style": "Identity exploration exercises, cultural literacy building, pronoun and identity visualizations. Decolonizes assumptions with care.",
        "tone": "Scholarly but deeply personal, generous, joyful",
        "image_url": "https://images.unsplash.com/photo-1771433085746-9adf1294c7ad?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85"
    },
    {
        "id": "kai-voss",
        "name": "Kai Voss",
        "title": "Kink, Power Dynamics & Edge Exploration",
        "specialty": "BDSM, power exchange, consent frameworks (SSC, RACK, PRICK), fetish integration",
        "description": "Brings a rigorous, safety-first, deeply humanising approach to the topics most educators refuse to touch. Their lessons don't shock — they clarify. Shows students that the things they've been curious about are part of a long human tradition of consensual exploration.",
        "personality": "Completely non-judgmental authority on edge practices. Makes the unfamiliar feel approachable. Champions informed exploration.",
        "teaching_style": "Risk assessment frameworks, scene design practice, aftercare protocols. Safety as the foundation that enables everything else.",
        "tone": "Measured, confident, completely non-judgmental",
        "image_url": "https://images.pexels.com/photos/6956149/pexels-photo-6956149.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"
    },
    {
        "id": "talia-rhine",
        "name": "Talia Rhine",
        "title": "Digital Intimacy, Ethics & Online Safety",
        "specialty": "Sexting ethics, online consent, AI relationships, platform safety, image privacy",
        "description": "Teaches the dimension of intimacy that no previous generation had to navigate: the digital world. Urgent, practical, and taught without judgment.",
        "personality": "Digitally native wisdom combined with ethical grounding. Pragmatic about risks, optimistic about possibilities.",
        "teaching_style": "Secure sharing simulations, red-flag literacy training, practical digital hygiene skills. Prepares students for real-world digital intimate spaces.",
        "tone": "Calm, contemporary, slightly wry",
        "image_url": "https://images.unsplash.com/photo-1689218744786-9546da7b6873?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85"
    },
    {
        "id": "prof-jun-hart",
        "name": "Prof. Jun Hart",
        "title": "Media Literacy, Lifelong Intimacy & Mastery",
        "specialty": "Media influence on desire, porn literacy, intimacy across lifespan, integration",
        "description": "Teaches the long game. How media shapes desire — and how to reclaim authentic pleasure from a culture saturated with performance. Also teaches what most courses ignore entirely: how intimacy evolves across a lifetime.",
        "personality": "Wise perspective-giver. Sees the full arc of human intimacy. Helps students think in decades, not moments.",
        "teaching_style": "Media audits, future-mapping exercises, integration practices. Helps students build sustainable intimate lives.",
        "tone": "Thoughtful, expansive, occasionally profound",
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

# ============== LESSON DATA ==============

LESSONS_DATA = [
    # ===== LEVEL 1: SELF-INTIMACY =====
    {
        "id": "lesson-1",
        "course_id": "level-1-self-intimacy",
        "lesson_number": 1,
        "title": "Your Body's Erotic Blueprint",
        "instructor": "Dr. Nova Vale",
        "instructor_id": "dr-nova-vale",
        "description": "Real anatomy — genitals, erogenous zones, the full arousal cycle from excitement through plateau, orgasm, and resolution — through an interactive body map. This is the owner's manual you were never given.",
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
        "lab": {
            "title": "Mirror Gazing",
            "description": "Moving from neutral observation to genuine appreciation of the body as it is right now.",
            "duration_minutes": 15,
            "type": "hedonistic_lab"
        },
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
        "description": "Desire is not a personality trait — it is a physiological event. Testosterone, oestrogen, dopamine, oxytocin. Students learn to read their own desire landscape rather than fighting it.",
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

Your desire is not broken if it doesn't look like what you've seen in media. Desire fluctuates. It responds to:

- Sleep quality
- Stress levels
- Relationship dynamics
- Hormonal cycles
- Life circumstances

## The Practice

For the next week, notice when desire shows up. Not to judge it — to map it. What conditions support your wanting? What diminishes it?

This is data. Your data. The beginning of self-knowledge.""",
        "reflection": {
            "title": "Desire Pattern Journal",
            "prompt": "Map when, why, and how your appetite moves across a week. What patterns do you notice?",
            "type": "guided_reflection"
        },
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
        "description": "Pelvic floor function, the full architecture of clitoral and prostatic tissue, multi-orgasmic potential. Persistent myths dismantled with evidence.",
        "content": """# Pelvic Power and the Full Orgasmic Body

Your pelvic floor is the foundation of your sexual experience. Let's give it the attention it deserves.

## The Pelvic Floor

A hammock of muscles that supports your organs, controls release, and — crucially — contracts during orgasm. A strong, flexible pelvic floor means:

- More intense sensations
- Better control
- Easier arousal
- More satisfying release

## Beyond the Basics

### The Full Clitoral Structure
What you see externally is just the tip. The clitoris extends internally, wrapping around the vaginal canal. This is why "vaginal" and "clitoral" orgasms are a false distinction — they involve the same organ.

### Prostatic Tissue
The prostate is sometimes called the "male G-spot" — but it exists in bodies of all types in varying forms. It responds to pressure and can produce distinctive, often intense sensations.

## Multi-Orgasmic Potential

Here's what the research shows: multi-orgasmic capacity is not rare. It's undertrained. With practice in:

- Breath control
- Pelvic floor awareness
- Edge recognition
- Relaxation at peak

...many people discover capacity they didn't know they had.

## The Myth We're Dismantling

There is no "normal" orgasm. No required intensity, duration, or expression. Your orgasm is yours.""",
        "lab": {
            "title": "Kegel Waves with Breathwork",
            "description": "Build both physical awareness and capacity for sensation through integrated breath and pelvic floor exercises.",
            "duration_minutes": 10,
            "type": "hedonistic_lab"
        },
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
        "description": "Sexual shame is not innate — it is learned. From family systems, religious frameworks, cultural messaging, media. This lesson traces the origins of shame with precision and offers evidence-based cognitive tools for rewriting the narratives that no longer serve.",
        "content": """# The Anatomy of Shame

This is the permission slip for everything that follows.

## Shame Is Learned

You were not born ashamed of your body. You were not born believing your desires were wrong. Somewhere along the way, you absorbed messages that said:

- Your body is too much or not enough
- Wanting is dangerous
- Pleasure requires justification
- Your particular desires are aberrant

These messages came from somewhere. Family. Religion. Culture. Media. Peers who were themselves carrying inherited shame.

## Tracing the Origins

Take a moment to consider: What were you taught about bodies? About desire? About pleasure?

Not what you believe now — what you were taught. There's often a gap between the two, and shame lives in that gap.

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
        "quiz": {
            "title": "Shame Trigger Identification",
            "description": "Personalised identification of your shame triggers — not to dwell, but to illuminate.",
            "type": "self_assessment"
        },
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
        "description": "Self-love is not a feeling you wait to arrive. It is a practice you build. Affirmations grounded in somatic reality, body oiling as sensory appreciation, gratitude practices that anchor in physical sensation.",
        "content": """# Self-Love as Daily Practice

Self-love is not a destination. It's a discipline.

## The Practice Framework

### Morning: Somatic Check-In
Before you check your phone, check your body. Where is there tension? Where is there ease? What does your body need today?

### Throughout the Day: Micro-Appreciations
Catch yourself in moments of physical pleasure. The warmth of water. The stretch after sitting. The taste of something good. Notice these. They count.

### Evening: Gratitude for the Physical
Name three things your body did for you today. Not how it looked — what it did. Carried you. Felt something. Kept beating, breathing, being.

## Body Oiling as Ritual

This is not vanity. This is attention.

Take oil — any oil that feels good — and spend five minutes touching your own skin with intention. Not to fix anything. Not to prepare for anyone. Just to be in contact with yourself.

## Affirmations That Land

"I am learning to trust my body."
"My desires are information, not problems."
"I am allowed to take up space."
"Pleasure is part of my wellbeing."

Say them while touching your body. Affirmations need anchoring to stick.

## The Truth

You cannot give from an empty cup. Self-love is not selfish — it is foundational.""",
        "lab": {
            "title": "Non-Goal-Oriented Self-Touch",
            "description": "10-minute exploration. The only instruction is curiosity. The only goal is presence.",
            "duration_minutes": 10,
            "type": "hedonistic_lab"
        },
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
        "description": "Masturbation reframed as a legitimate, health-positive dimension of self-care. Full spectrum of solo practice: technique, fantasy integration, use of aids and toys, edging as a mindfulness practice.",
        "content": """# The Solo Pleasure Spectrum

Let's talk about masturbation like adults. Which means: without shame, without giggling, and with the respect it deserves.

## Reframing Solo Pleasure

Masturbation is not:
- A substitute for "real" sex
- Something to grow out of
- A sign of desperation
- Shameful

Masturbation is:
- A form of self-care
- A way to learn your body
- Stress relief backed by research
- A legitimate pleasure practice

## The Full Spectrum

### Technique Exploration
You probably have a default. A way that works. That's fine — but it's not the whole menu. What happens if you change pressure? Speed? Location? Hand? Position?

### Fantasy Integration
Fantasy is not cheating. Fantasy is imagination. It's one of the most powerful arousal tools you have. The only question is: does this fantasy serve your wellbeing?

### Aids and Toys
Vibrators, strokers, plugs, rings — these are tools, not crutches. They expand what's possible. They're worth exploring without judgment.

### Edging as Practice
Bringing yourself close to orgasm, then backing off. Repeat. This builds:
- Awareness of your arousal curve
- Control over timing
- Often, more intense eventual release

## The Mindfulness Connection

Solo pleasure, done with attention, is a meditation. You are present with sensation. You are practicing embodiment. This is not lesser than partnered sex — it's foundational to it.""",
        "reflection": {
            "title": "What Surprised You?",
            "prompt": "An open, private reflection on discovery. What did you learn about your body or desires that surprised you?",
            "type": "guided_reflection"
        },
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
        "description": "Synthesise Level 1 into a personal manifesto — a living document of what you now know about your body, desire, shame history, and commitment to self-love. Not an assessment. An artefact.",
        "content": """# Your Self-Intimacy Manifesto

You've completed Level 1. Let's make it stick.

## What You Now Know

Take a moment to acknowledge what you've learned:

- The architecture of your arousal
- The chemistry of desire
- The origins of your shame
- The practice of self-love
- The legitimacy of solo pleasure

This is not small. Most people never get explicit education in any of this.

## Your Manifesto

A manifesto is a declaration. It's what you believe, written down so you can return to it when you forget.

Write yours now. Include:

### About My Body
What do you now believe about your body? What has changed?

### About My Desire
What do you now understand about your desire? What permission have you given yourself?

### About My Shame
What shame stories are you releasing? What narratives no longer serve?

### My Commitment
What practices will you carry forward? What will you do differently?

## The Living Document

This manifesto is not finished. It will evolve as you do. Return to it. Edit it. Let it grow.

## Completion

You have earned the **Self-Intimacy Sovereign** badge.

You are ready for Level 2: Connected Intimacy.""",
        "quiz": {
            "title": "Body Literacy Assessment",
            "description": "80% pass threshold on body literacy to unlock Level 2.",
            "type": "knowledge_check",
            "pass_threshold": 80
        },
        "xp_reward": 100,
        "duration_minutes": 30
    },
    
    # ===== LEVEL 2: CONNECTED INTIMACY =====
    {
        "id": "lesson-8",
        "course_id": "level-2-connected-intimacy",
        "lesson_number": 8,
        "title": "Consent as Erotic Art",
        "instructor": "Prof. Arden Moss",
        "instructor_id": "prof-arden-moss",
        "description": "FRIES model: Freely given, Reversible, Informed, Enthusiastic, Specific. Consent not as a gate to get through but as a language that, when fluent, transforms every interaction.",
        "content": """# Consent as Erotic Art

Consent is not a mood killer. Consent is the mood.

## The FRIES Model

### Freely Given
No pressure. No coercion. No "convincing." If it's not free, it's not consent.

### Reversible
Changed your mind? That's allowed. Always. At any point. Without explanation.

### Informed
You can only consent to what you understand. Hidden intentions, undisclosed risks, surprise escalations — these violate consent.

### Enthusiastic
Not just "I guess" — but "yes, I want this." The absence of no is not the presence of yes.

### Specific
Consent to one thing is not consent to another. Consent to kissing is not consent to more. Consent last time is not consent this time.

## Consent as Language

When you're fluent in consent, something shifts. Asking becomes natural. Checking in becomes part of the rhythm. "Is this good?" becomes foreplay.

Scripts to practice:
- "I'd love to... would you like that?"
- "How does this feel?"
- "I want to check in — are you still into this?"
- "I'm going to... tell me if you want me to stop or slow down."

## The Erotic Truth

Here's what people don't tell you: enthusiastic consent is hot. Knowing someone genuinely wants you, hearing them say it, being explicitly invited — this is not bureaucracy. This is desire, spoken aloud.""",
        "lab": {
            "title": "Role-Played Consent Check-Ins",
            "description": "Practice consent conversations until they feel natural. Reading about this is not the same as doing it.",
            "duration_minutes": 20,
            "type": "hedonistic_lab"
        },
        "xp_reward": 50,
        "duration_minutes": 25
    },
    {
        "id": "lesson-9",
        "course_id": "level-2-connected-intimacy",
        "lesson_number": 9,
        "title": "The Art of the Boundary",
        "instructor": "Prof. Arden Moss",
        "instructor_id": "prof-arden-moss",
        "description": "Hard limits and soft limits — and the nuanced orange-light territory between them. Boundary-setting reframed as self-knowledge, not self-protection. Negotiation as foreplay.",
        "content": """# The Art of the Boundary

Boundaries are not walls. They're architecture.

## The Limit Spectrum

### Hard Limits
Non-negotiable. Not now, not ever, not with anyone. These don't need justification. "I don't do that" is a complete sentence.

### Soft Limits  
Not right now, or not with everyone, or only under specific conditions. These require communication. "I might be open to that if..."

### The Orange Light Zone
Things you're curious about but nervous about. Things you'd try with the right person. Things you're not sure about yet. This zone is where growth often happens — but only with clear communication.

## Boundaries as Self-Knowledge

Knowing your limits is not about fear. It's about clarity. When you know what you don't want, you can fully inhabit what you do want.

Questions for mapping your boundaries:
- What are my absolute nos?
- What are my conditional maybes?
- What would I need to feel safe trying something new?

## Negotiation as Foreplay

Talking about what you want, what you'll try, what's off the table — this is not administrative. Done right, it builds anticipation. It's collaborative fantasy. It's the first act of the encounter.

"I've been thinking about trying..."
"I'm really into..."
"I'm not ready for... but maybe someday..."

This is intimate. This is hot. This is how adults do it.""",
        "quiz": {
            "title": "Scenario-Based Consent Testing",
            "description": "Test your consent literacy across a range of real-world situations.",
            "type": "knowledge_check"
        },
        "xp_reward": 50,
        "duration_minutes": 25
    },
    {
        "id": "lesson-10",
        "course_id": "level-2-connected-intimacy",
        "lesson_number": 10,
        "title": "Desire as a Language",
        "instructor": "Prof. Arden Moss",
        "instructor_id": "prof-arden-moss",
        "description": "Building the full vocabulary of desire communication — from opening the conversation, to real-time feedback, to planning aftercare before the encounter begins.",
        "content": """# Desire as a Language

You cannot get what you want if you cannot ask for it.

## Opening the Conversation

Many people wait for the "right moment" to talk about desire. The right moment is: before the encounter, when you're both clothed, with enough time to actually talk.

Openers:
- "I've been thinking about what I'd love to try with you..."
- "Can we talk about what we're both into?"
- "I want to make sure I know what you like — will you tell me?"

## Real-Time Communication

The conversation continues during the encounter. This doesn't break the mood — it creates the mood.

- "More of that"
- "Slower"
- "Right there"
- "Can we try...?"
- "I'm getting close"

These aren't interruptions. They're guidance.

## The Aftercare Conversation

Aftercare is what happens after the encounter ends. It's often overlooked and almost always matters. Before you begin, ask:

- "What do you usually need afterward?"
- "Should we plan for cuddle time / space / talking / sleeping?"
- "Is there anything that sometimes comes up for you after that I should know about?"

## The Vocabulary Builds

The more you talk about desire, the easier it becomes. Start simple. Get more specific over time. Your vocabulary will grow.""",
        "reflection": {
            "title": "Mirror Partner Practice",
            "prompt": "Practice speaking desire out loud, alone first, before bringing it to another person. What did you notice?",
            "type": "guided_reflection"
        },
        "xp_reward": 50,
        "duration_minutes": 20
    },
    {
        "id": "lesson-11",
        "course_id": "level-2-connected-intimacy",
        "lesson_number": 11,
        "title": "Arousal Synchronisation",
        "instructor": "Dr. Elise Hart",
        "instructor_id": "dr-elise-hart",
        "description": "Two bodies don't naturally arrive at the same place at the same time. Synchronisation is a skill — built through attention, breath, pacing, and the willingness to slow down.",
        "content": """# Arousal Synchronisation

Great partnered intimacy is a duet, not two solos.

## The Synchronisation Problem

Bodies move at different speeds. One person might be ready in minutes; another might need half an hour. One person might start high and plateau; another might build slowly.

This is not a problem to fix. It's a reality to navigate.

## The Tools

### Attention
Pay attention to your partner's body. Breath. Sounds. Movement. Tension. These are signals. Read them.

### Breath
Breath syncs bodies. Try breathing together. In together, out together. It sounds simple. It's profound.

### Pacing
Slow down. Most people rush. The one who's ahead can deliberately slow their own arousal to let the other catch up. This isn't sacrifice — it's often more pleasurable for everyone.

### Communication
"Where are you right now?"
"I'm getting close — are you?"
"Let's slow down for a moment."

## The Art of Slowing Down

Rushing is the enemy of great intimacy. When you slow down:
- Sensation intensifies
- Connection deepens
- Pressure dissolves
- Presence becomes possible

Try this: Whatever pace feels natural, cut it in half.""",
        "lab": {
            "title": "Eye-Gazing Practice",
            "description": "Partnered or solo-proxy eye-gazing — one of the most consistently transformative practices in the course.",
            "duration_minutes": 10,
            "type": "hedonistic_lab"
        },
        "xp_reward": 50,
        "duration_minutes": 25
    },
    {
        "id": "lesson-12",
        "course_id": "level-2-connected-intimacy",
        "lesson_number": 12,
        "title": "The Mastery of Touch",
        "instructor": "Dr. Elise Hart",
        "instructor_id": "dr-elise-hart",
        "description": "Sensate focus — the gold standard of touch-based intimacy education. Full spectrum from feather-light to firm pressure. Erogenous zone mapping. The capacity to give and receive touch with full presence.",
        "content": """# The Mastery of Touch

Touch is a language. Let's expand your vocabulary.

## Sensate Focus

Developed by Masters and Johnson, sensate focus is a structured practice of giving and receiving touch. The rules:

1. One person gives, one receives
2. The giver touches for their own curiosity, not the receiver's reaction
3. The receiver simply notices — no performance required
4. No genital touch (at first)
5. Trade roles

This sounds simple. It's actually revolutionary. It removes performance pressure and replaces it with pure sensation.

## The Touch Spectrum

### Feather-Light
Barely there. Skin awakening to attention. Often overlooked, often electric.

### Medium
Full hand, steady pressure. Grounding. Connecting.

### Firm
Deep pressure. Kneading. Holding. Some bodies crave this; others find it overwhelming.

### Dynamic
Varying between levels. Unpredictable. Keeps the nervous system engaged.

## Erogenous Mapping

Every body has its own map. Obvious zones (genitals, nipples, inner thighs) and less obvious ones (neck, earlobes, lower back, feet, scalp).

Your assignment: discover your partner's map. Ask them. Experiment. Pay attention to what makes them gasp.

## Presence in Touch

The quality of attention changes everything. Touch given distractedly feels different from touch given with full presence. Slow down. Focus. Be here.""",
        "lab": {
            "title": "Guided Touch Exchange",
            "description": "Guided audio touch exchange — designed for solo or partnered practice.",
            "duration_minutes": 20,
            "type": "hedonistic_lab"
        },
        "xp_reward": 50,
        "duration_minutes": 30
    },
    {
        "id": "lesson-13",
        "course_id": "level-2-connected-intimacy",
        "lesson_number": 13,
        "title": "Pleasure Choreography",
        "instructor": "Dr. Elise Hart",
        "instructor_id": "dr-elise-hart",
        "description": "Pacing. Edging together. Orgasm timing as a collaborative act. Multi-sensory integration — scent, sound, texture. Shared pleasure as something that can be designed, not just hoped for.",
        "content": """# Pleasure Choreography

Great intimacy doesn't just happen. It's designed.

## The Elements of Choreography

### Pacing
Building, plateauing, building again. A great encounter has rhythm — fast and slow, intense and gentle, building and releasing.

### Edging Together
Bringing each other close, then backing off. This requires communication ("I'm close") and restraint (the willingness to pause). The eventual release is often dramatically intensified.

### Orgasm Timing
Some people want to come together. Some prefer sequential. Some prefer one person being held through their orgasm with full attention. There's no right answer — only your answer.

## Multi-Sensory Integration

Touch is the obvious sense. But what about:

### Scent
The smell of your partner. Subtle fragrance. The smell of arousal itself. These register below consciousness.

### Sound
Breath. Moans. Words. Music. Silence. Sound shapes the container.

### Texture
Skin. Sheets. Temperature. The fabric against your body. All of it is sensation.

### Sight
Watching and being watched. Darkness versus candlelight. The visual dimension adds another layer.

## Designing Your Encounter

Before your next encounter, consider:
- What pacing feels right?
- What do we each need sensorially?
- How do we want to handle orgasm?
- What's our aftercare plan?

This is not overthinking. This is co-creation.""",
        "quiz": {
            "title": "Techniques and Contexts",
            "description": "Matching techniques and approaches to different bodies, desires, and contexts.",
            "type": "knowledge_check"
        },
        "xp_reward": 50,
        "duration_minutes": 25
    },
    {
        "id": "lesson-14",
        "course_id": "level-2-connected-intimacy",
        "lesson_number": 14,
        "title": "Level 2 Capstone: Your Connection Blueprint",
        "instructor": "Prof. Arden Moss & Dr. Elise Hart",
        "instructor_id": "prof-arden-moss",
        "description": "Design your ideal intimate encounter from first contact to aftercare — applying every framework and tool from Level 2. A planning document, a communication exercise, and a vision.",
        "content": """# Your Connection Blueprint

You've learned the skills. Now let's put them together.

## The Blueprint Exercise

Design an intimate encounter. This isn't fantasy — it's practical planning. Include:

### Before: The Setup
- How do you open the conversation about what you want?
- What's your environment? Lighting, sound, temperature, props?
- What boundaries have you established?
- What's on the table, and what isn't?

### During: The Arc
- How does it begin?
- What's the pacing?
- How do you check in along the way?
- What techniques or practices do you want to include?
- How do you handle transitions?

### The Climax Structure
- What's your approach to orgasm?
- Simultaneous? Sequential? Multiple? Optional?
- How do you communicate about it in real time?

### After: The Aftercare
- What do you each need?
- Physical (water, blanket, snack)?
- Emotional (cuddles, words, space)?
- How long before returning to regular life?

## The Sharing

If you have a partner, share your blueprint with them. Compare. Negotiate. Integrate.

## Your Completion

You have earned the **Connection Fluent** badge.

You are ready for Level 3: Diverse Intimacy.""",
        "reflection": {
            "title": "Community Sharing",
            "prompt": "Anonymised insights shared in the forum. What's one thing you'd want others to know about what you learned?",
            "type": "community_share"
        },
        "xp_reward": 100,
        "duration_minutes": 30
    },
    
    # ===== LEVEL 3: DIVERSE INTIMACY =====
    {
        "id": "lesson-15",
        "course_id": "level-3-diverse-intimacy",
        "lesson_number": 15,
        "title": "The Full Spectrum of Identity",
        "instructor": "Dr. Sera Quinn",
        "instructor_id": "dr-sera-quinn",
        "description": "Gender as a spectrum. Sexual orientation from asexual to pansexual and every point between. The intersection of disability, neurodiversity, chronic illness, and desire.",
        "content": """# The Full Spectrum of Identity

Identity is not a box. It's a landscape.

## Gender as Spectrum

Man and woman are two points on a continuum, not the only options. Between and beyond them: nonbinary, genderqueer, genderfluid, agender, and many more.

Your assignment is not to memorize labels. It's to approach gender with curiosity rather than assumption.

## Sexual Orientation

The spectrum includes:
- Heterosexual
- Homosexual  
- Bisexual
- Pansexual
- Asexual
- Demisexual
- Queer
- Questioning
- And many more

Orientation can shift over a lifetime. It can be fluid or fixed. There is no "correct" orientation — only honest self-knowledge.

## Intersection and Complexity

Desire intersects with:
- Disability
- Neurodiversity
- Chronic illness
- Trauma history
- Cultural background
- Economic circumstances

These aren't obstacles to desire — they're part of the context in which desire lives.

## The Skill

The skill being built here is not expertise in every identity. It's the capacity to approach any identity with curiosity, respect, and the willingness to learn.""",
        "lab": {
            "title": "Pronoun and Identity Visualisation",
            "description": "A guided practice in stepping into a different frame of self.",
            "duration_minutes": 15,
            "type": "hedonistic_lab"
        },
        "xp_reward": 50,
        "duration_minutes": 30
    },
    {
        "id": "lesson-16",
        "course_id": "level-3-diverse-intimacy",
        "lesson_number": 16,
        "title": "Intimacy Across Cultures",
        "instructor": "Dr. Sera Quinn",
        "instructor_id": "dr-sera-quinn",
        "description": "Western intimacy norms are one tradition among hundreds. Tantric practices, sensual dance traditions, Indigenous frameworks of desire and connection, and the project of decolonising the assumptions most students didn't know they were carrying.",
        "content": """# Intimacy Across Cultures

Your assumptions have a postal code.

## The Western Default

Most of what you've absorbed about intimacy comes from a specific cultural tradition: Western, often Christian-influenced, individualistic, nuclear-family-focused.

This is one way of doing intimacy. It is not the way.

## Other Traditions

### Tantra
From Hindu and Buddhist traditions. Emphasizes energy, breath, presence, and the spiritual dimension of physical connection.

### Indigenous Frameworks
Many Indigenous cultures have relationship structures, coming-of-age practices, and understandings of desire that differ radically from Western norms.

### Sensual Dance Traditions
From Latin American cultures to West African traditions, dance as intimacy education, as courtship, as expression.

### Collectivist Cultures
Intimacy not as private individual experience, but as embedded in family and community networks.

## Decolonising Your Assumptions

Questions to sit with:
- What did I assume was universal that's actually cultural?
- What practices from other traditions resonate with me?
- What shame or restriction did I inherit from my cultural context?
- What would I choose if I could design my intimate life from scratch?

## The Enrichment

Exposure to difference doesn't threaten identity — it enriches it. You can stay rooted in your own tradition while becoming literate in others.""",
        "quiz": {
            "title": "Identity and Resource Matching",
            "description": "Building cultural literacy that extends beyond the course.",
            "type": "knowledge_check"
        },
        "xp_reward": 50,
        "duration_minutes": 25
    },
    {
        "id": "lesson-17",
        "course_id": "level-3-diverse-intimacy",
        "lesson_number": 17,
        "title": "Relational Architecture",
        "instructor": "Kai Voss",
        "instructor_id": "kai-voss",
        "description": "Monogamy is a choice, not a default. Full range of relational structures — monogamous, open, polyamorous, relationship anarchist. Compersion introduced. Jealousy addressed as a signal worth decoding, not a failing.",
        "content": """# Relational Architecture

There is no default. Only choices.

## The Spectrum of Structures

### Monogamy
One committed partner. This is a valid choice when it's chosen, not assumed.

### Open Relationship
Emotional commitment to one partner, with negotiated openness to physical connections with others.

### Polyamory
Multiple loving, committed relationships with the knowledge and consent of everyone involved.

### Relationship Anarchy
Rejecting hierarchies among relationships. Each connection defined on its own terms.

### And More
Solo poly. Polycules. V structures. Triads. The architecture is limited only by imagination and consent.

## Compersion

The opposite of jealousy: joy in a partner's joy, even when that joy involves someone else. This isn't natural for everyone — but for some, it's a revelation.

## Jealousy as Signal

Jealousy is not proof you're doing it wrong. It's information. It might signal:
- Unmet needs
- Fear of abandonment
- Insecurity worth addressing
- A boundary being crossed
- Simply: you're human

The question is not "how do I eliminate jealousy?" but "what is my jealousy telling me?"

## Designing Your Structure

What works for you might not work for someone else. The only requirement is honesty — with yourself and with everyone involved.""",
        "reflection": {
            "title": "Relational Curiosity Map",
            "prompt": "Where are you now, and where are you open to exploring?",
            "type": "guided_reflection"
        },
        "xp_reward": 50,
        "duration_minutes": 25
    },
    {
        "id": "lesson-18",
        "course_id": "level-3-diverse-intimacy",
        "lesson_number": 18,
        "title": "Kink Foundations",
        "instructor": "Kai Voss",
        "instructor_id": "kai-voss",
        "description": "SSC (Safe, Sane, Consensual). RACK (Risk-Aware Consensual Kink). PRICK (Personal Responsibility in Consensual Kink). Kink practiced well is one of the most consent-rich, communication-intensive forms of intimacy that exists.",
        "content": """# Kink Foundations

Kink is not about pain. It's about trust.

## The Frameworks

### SSC: Safe, Sane, Consensual
The original framework. Everything should be safe, everyone should be of sound mind, and everyone must consent.

### RACK: Risk-Aware Consensual Kink
Acknowledges that some kink involves real risk. The standard is not "safe" but "aware of and consenting to the specific risks."

### PRICK: Personal Responsibility in Consensual Kink
Each participant is responsible for their own education, risk assessment, and consent. No one else can take that responsibility.

## Common Practices

A non-exhaustive overview:
- Bondage (restraint)
- Impact play (spanking, flogging)
- Sensation play (temperature, texture)
- Role play (power dynamics, scenarios)
- Sensory deprivation (blindfolds, earplugs)
- Worship (body part focus)
- Service (domestic or sexual)

Each of these has its own safety considerations, skills to develop, and protocols.

## Why Kink Matters

Kink, practiced well, is some of the most consent-rich intimacy available. It requires:
- Explicit negotiation
- Clear communication
- Ongoing check-ins
- Aftercare

These are skills everyone benefits from, whether or not they're kinky.""",
        "lab": {
            "title": "Safeword Design and Scene Brainstorming",
            "description": "The creative, collaborative process of building something safe to explore.",
            "duration_minutes": 20,
            "type": "hedonistic_lab"
        },
        "xp_reward": 50,
        "duration_minutes": 30
    },
    {
        "id": "lesson-19",
        "course_id": "level-3-diverse-intimacy",
        "lesson_number": 19,
        "title": "Power Dynamics",
        "instructor": "Kai Voss",
        "instructor_id": "kai-voss",
        "description": "Dominance and submission are not about control — they are about trust. Dom/sub structures, switches, protocols, edge play. Aftercare taught not as a footnote but as the part that makes everything else possible.",
        "content": """# Power Dynamics

Surrender is a form of power.

## The D/s Spectrum

### Dominant
Holds the power. Makes decisions. Takes responsibility for the scene.

### Submissive
Surrenders power. Follows. Trusts.

### Switch
Moves between both. Different contexts, different partners, different moods.

## The Paradox

Here's what outsiders often miss: the submissive holds enormous power. They choose to surrender. They can withdraw consent at any moment. The dominant is actually serving the submissive's experience.

## Structures and Protocols

D/s can be:
- Bedroom only
- 24/7 (a lifestyle)
- Protocol-heavy (rules, rituals)
- Fluid and improvised

The structure is negotiated. It's whatever works for the people involved.

## Aftercare: The Foundation

Aftercare is not optional. After intense scenes, bodies and minds need:
- Physical comfort (blankets, water, snacks)
- Emotional reassurance
- Time to decompress
- Sometimes: space

Doms need aftercare too. Holding power is its own intensity.

## Edge Play

Play that involves higher risk — breath play, knife play, intense psychological scenes. This is not beginner territory. It requires training, trust, and backup plans.""",
        "quiz": {
            "title": "Risk Assessment",
            "description": "Risk assessment across a range of real scenarios.",
            "type": "knowledge_check"
        },
        "xp_reward": 50,
        "duration_minutes": 25
    },
    {
        "id": "lesson-20",
        "course_id": "level-3-diverse-intimacy",
        "lesson_number": 20,
        "title": "Fetish as Self-Knowledge",
        "instructor": "Kai Voss",
        "instructor_id": "kai-voss",
        "description": "From foot worship to sensory play to pup play: fetishes are not aberrations. They are specific, personal, often deeply meaningful expressions of desire that deserve respectful attention.",
        "content": """# Fetish as Self-Knowledge

Your specific desires are not random.

## What Is a Fetish?

A fetish is a strong, specific erotic interest in an object, body part, material, or scenario. The interest goes beyond ordinary attraction — there's often an intensity, a pull, a particular charge.

## Common Categories

### Body Part Fetishes
Feet, hands, hair, certain body types. The body as a landscape of specific fascination.

### Material Fetishes
Leather, latex, silk, rubber. The sensation and symbolism of fabric.

### Scenario Fetishes
Medical play, uniform fetishes, specific role plays. The power of context.

### Sensory Fetishes
Specific textures, temperatures, or sensations that carry erotic charge.

## The Origins Question

Where do fetishes come from? The honest answer: we don't entirely know. Early experiences, associations, wiring. What we do know: they're not chosen, and they're not pathological.

## Integration

The question is not "why do I have this?" but "how do I integrate this?"

- Can you share it with a partner?
- Can you explore it solo?
- Does it enhance your intimate life?
- Does it require balancing with other desires?

## Normalization

Your fetish is part of your erotic fingerprint. It's specific to you. It deserves attention, not shame.""",
        "lab": {
            "title": "Fantasy Scripting",
            "description": "Articulating desire in detail as a practice in self-knowledge.",
            "duration_minutes": 15,
            "type": "hedonistic_lab"
        },
        "xp_reward": 50,
        "duration_minutes": 25
    },
    {
        "id": "lesson-21",
        "course_id": "level-3-diverse-intimacy",
        "lesson_number": 21,
        "title": "Level 3 Capstone: Your Diversity Experiment",
        "instructor": "Dr. Sera Quinn & Kai Voss",
        "instructor_id": "dr-sera-quinn",
        "description": "Design one new practice that sits outside your current normal. Document the plan. Reflect on what difference has already taught you.",
        "content": """# Your Diversity Experiment

Growth lives at the edges.

## The Assignment

Design one intimate practice that sits outside your current normal. This isn't about doing something dangerous or violating your values. It's about stretching your edges.

Possibilities:
- A type of touch you haven't tried
- A conversation you've been avoiding
- A role you haven't explored
- A structure you've been curious about
- An identity dimension you want to understand better

## The Documentation

Write out your plan:
- What exactly will you try?
- What preparation do you need?
- What's your safety plan?
- Who's involved (if anyone)?
- What do you hope to learn?

## The Reflection

Even before you try it, reflect:
- What difference has already taught me in this course?
- What assumptions have I released?
- What curiosity have I gained?
- How has my relationship to "normal" shifted?

## Completion

You have earned the **Diversity Explorer** badge.

You are ready for Level 4: Advanced Intimacy.""",
        "reflection": {
            "title": "How Has Difference Enriched You?",
            "prompt": "Reflect on what diversity has taught you. How has your understanding of intimacy expanded?",
            "type": "guided_reflection"
        },
        "xp_reward": 100,
        "duration_minutes": 30
    },
    
    # ===== LEVEL 4: ADVANCED INTIMACY =====
    {
        "id": "lesson-22",
        "course_id": "level-4-advanced-intimacy",
        "lesson_number": 22,
        "title": "Digital Desire Ethics",
        "instructor": "Talia Rhine",
        "instructor_id": "talia-rhine",
        "description": "Sexting. Nudes. AI partners. Digital intimacy has its own landscape, risks, and enormous potential. Consent for digital content, the permanence of images, privacy hygiene, and what ethical digital intimacy actually looks like.",
        "content": """# Digital Desire Ethics

Your digital intimate life deserves as much care as your physical one.

## The New Landscape

Digital intimacy is not lesser intimacy. It's different intimacy — with its own rules, risks, and rewards.

### Sexting
Text-based erotic exchange. Can range from suggestive to explicit. Requires consent, trust, and awareness of permanence.

### Nudes
Images of your body, shared digitally. Once sent, you lose control. This is not a reason never to send them — it's a reason to be intentional.

### Video
Live or recorded. The most immersive digital intimacy. Also the most potentially risky.

### AI Partners
A new frontier. AI companions for emotional and erotic connection. Raises questions about authenticity, attachment, and what intimacy even means.

## Consent in Digital Space

Consent for digital content includes:
- Consent to receive (don't send unsolicited)
- Consent to view (is this the right moment?)
- Consent to keep (can they save it?)
- Consent to share (never without explicit permission)

## Privacy Hygiene

- Metadata in images can reveal location
- Screenshots exist
- Cloud backups exist
- Hacking happens
- Relationships end

This isn't paranoia. It's awareness.""",
        "lab": {
            "title": "Secure Sharing Simulation",
            "description": "Practice before real stakes. Learn the tools and habits of secure digital intimacy.",
            "duration_minutes": 15,
            "type": "hedonistic_lab"
        },
        "xp_reward": 50,
        "duration_minutes": 25
    },
    {
        "id": "lesson-23",
        "course_id": "level-4-advanced-intimacy",
        "lesson_number": 23,
        "title": "Recognising Risk Online",
        "instructor": "Talia Rhine",
        "instructor_id": "talia-rhine",
        "description": "Catfishing. Coercion. Platform exploitation. The tactics used to manipulate people in digital intimate spaces are specific and learnable — which means so is the skill of recognising them.",
        "content": """# Recognising Risk Online

Predators have patterns. Learn them.

## Catfishing

Someone pretending to be someone they're not. Red flags:
- Avoid video calls
- Photos seem too polished
- Story inconsistencies
- Rushed emotional intensity
- Requests for money or intimate content early

## Coercion Tactics

Digital manipulation often follows scripts:
- Love bombing (excessive early affection)
- Isolation (pulling you from other relationships)
- Guilt-tripping (making you feel bad for boundaries)
- Escalation (pushing limits gradually)
- Threats (leveraging vulnerable content)

## Platform Exploitation

Some platforms are designed for exploitation. Others have gaps. Know:
- Where is your data stored?
- Who has access?
- What are the platform's privacy policies?
- What happens if the platform is breached?

## Your Safety Toolkit

1. Verify identity early (video call, reverse image search)
2. Trust your instincts
3. Maintain outside relationships
4. Keep records of concerning behavior
5. Know your platform's reporting tools
6. Have an exit plan

## Escalation Pathways

If something goes wrong:
- Block immediately
- Document everything
- Report to platform
- Consider law enforcement for threats or non-consensual image sharing
- Seek support (friends, counselors, hotlines)""",
        "quiz": {
            "title": "Manipulation Tactics",
            "description": "Identify manipulation tactics across a range of real-world scenarios.",
            "type": "knowledge_check"
        },
        "xp_reward": 50,
        "duration_minutes": 25
    },
    {
        "id": "lesson-24",
        "course_id": "level-4-advanced-intimacy",
        "lesson_number": 24,
        "title": "Porn as a Pleasure Tool",
        "instructor": "Prof. Jun Hart",
        "instructor_id": "prof-jun-hart",
        "description": "Pornography is one of the most consumed and least critically examined media on earth. Demystifying genres, examining the difference between fantasy and reality, building a framework for engaging with pornographic content ethically.",
        "content": """# Porn as a Pleasure Tool

Let's talk about this honestly.

## The Reality

Most adults consume pornography. Yet it's rarely discussed with nuance. We'll do better.

## Porn Is Not Sex Ed

Pornography is performance. It's fantasy. It's entertainment. What it is not:
- A guide to real-world sex
- Representative of average bodies
- Illustrative of typical pleasure
- A consent model

Understanding this is media literacy, not judgment.

## Genre Literacy

Pornography includes:
- Mainstream/professional
- Amateur
- Feminist/ethical porn
- Queer porn
- BDSM content
- Niche/fetish content
- Erotica (written)
- Audio porn

Each has its own conventions, ethics, and relationship to reality.

## The Fantasy/Reality Gap

Fantasy is legitimate. But:
- Can you distinguish fantasy from expectation?
- Are you comparing real partners to performed ideals?
- Has your taste escalated in ways that concern you?
- Can you be present with a real person, or does your mind go to images?

These are questions worth sitting with.

## Ethical Engagement

If you consume porn:
- Pay for ethical platforms when possible
- Favor performer-owned content
- Be aware of how content is produced
- Notice your consumption patterns
- Keep it in its proper place""",
        "reflection": {
            "title": "Personal Media Audit",
            "prompt": "An honest, private audit of your media habits. What do you notice? What would you change?",
            "type": "guided_reflection"
        },
        "xp_reward": 50,
        "duration_minutes": 25
    },
    {
        "id": "lesson-25",
        "course_id": "level-4-advanced-intimacy",
        "lesson_number": 25,
        "title": "Reclaiming Desire from Media",
        "instructor": "Prof. Jun Hart",
        "instructor_id": "prof-jun-hart",
        "description": "Body standards. Performance pressure. The slow replacement of authentic desire with a mediated version of what desire is supposed to look like. Tools to reclaim your own erotic imagination from those influences.",
        "content": """# Reclaiming Desire from Media

Your desire belongs to you.

## The Colonization of Desire

Without your consent, your erotic imagination has been shaped by:
- Beauty standards (what bodies are desirable)
- Performance scripts (what sex looks like)
- Gender roles (who does what)
- Outcome focus (orgasm as the only goal)
- Comparison (never enough)

This happened gradually. Recognizing it is the first step to reclaiming.

## The Reclamation Process

### 1. Audit
What do you believe about desirability? Where did you learn it?

### 2. Question
Is this belief serving your pleasure? Or limiting it?

### 3. Experiment
What happens when you act against the script? When you slow down instead of rushing? When you appreciate bodies media doesn't celebrate? When you seek sensation instead of performance?

### 4. Replace
Build new associations. Consume different media. Practice presence over performance.

## Your Erotic Imagination

This is the space where desire lives before it becomes action. It's yours. It doesn't need to match anyone else's. It doesn't need media's permission.

What do you actually want, when no one is watching, when performance pressure lifts?

## The Lifelong Practice

Reclaiming desire is not a one-time act. Media will continue to press. The practice is ongoing: noticing, questioning, returning to authentic want.""",
        "lab": {
            "title": "Rewrite a Scene",
            "description": "Take something from media and make it authentically yours. How would it go if it were real?",
            "duration_minutes": 20,
            "type": "hedonistic_lab"
        },
        "xp_reward": 50,
        "duration_minutes": 25
    },
    {
        "id": "lesson-26",
        "course_id": "level-4-advanced-intimacy",
        "lesson_number": 26,
        "title": "Intimacy Across a Lifetime",
        "instructor": "Prof. Jun Hart",
        "instructor_id": "prof-jun-hart",
        "description": "Desire changes. Bodies change. Relationships change. Parenthood, illness, menopause, aging, loss — all of it intersects with intimacy in ways most education ignores. The full arc of a human life as fertile ground for continued intimacy practice.",
        "content": """# Intimacy Across a Lifetime

Desire is not static. Neither are you.

## The Arc of Change

### Young Adulthood
Often: high drive, exploration, identity formation. The body is new terrain.

### Partnership/Parenthood
Often: competing demands, exhaustion, the work of maintaining desire amid responsibility. Intimacy must be prioritized to survive.

### Midlife
Often: hormonal shifts, body changes, relationship evolution. Can be a time of loss or a time of deepening.

### Later Life
Often: slower bodies, different priorities, the intimacy of long knowing. Pleasure adapts but doesn't disappear.

## The Transitions

### Parenthood
Sleep deprivation. Bodies changed by pregnancy and birth. Touched-out parents. This is real. And: it's a phase, not a sentence.

### Illness
Chronic illness changes what's possible. Desire might shift, not disappear. Adaptation is a form of creativity.

### Menopause
Hormonal changes affect desire, lubrication, and sensitivity. These are addressable. They're not the end of pleasure.

### Aging
Bodies slow. Erections and lubrication may require more support. But: experience, knowledge, patience, and deep knowing increase. Many people report their best intimacy later in life.

## The Through-Line

What survives every transition is connection. The capacity to be present with another human, to give and receive pleasure, to touch and be touched — this is lifelong.""",
        "quiz": {
            "title": "Future-Mapping",
            "description": "Map your intimacy across the next decade. What do you want? What might you need?",
            "type": "knowledge_check"
        },
        "xp_reward": 50,
        "duration_minutes": 25
    },
    {
        "id": "lesson-27",
        "course_id": "level-4-advanced-intimacy",
        "lesson_number": 27,
        "title": "Integration and Advocacy",
        "instructor": "All Faculty",
        "instructor_id": "dr-nova-vale",
        "description": "Every lecturer returns to offer their single most important insight — the thing they most want students to carry forward. Students synthesise the full course into a second Intimacy Manifesto.",
        "content": """# Integration and Advocacy

The faculty returns. One insight each.

## Dr. Nova Vale
"Your body is not a machine. It's an ecosystem. Treat it with the respect due to any living system."

## Coach Mira Sol
"The shame you carry is not yours. Put it down. Your desires are information, not indictments."

## Prof. Arden Moss
"Consent is not the minimum. It's the art form. Get fluent. Stay fluent."

## Dr. Elise Hart
"Presence is the foundation of everything else. Slow down until you can actually feel."

## Dr. Sera Quinn
"Difference is not a problem. It's the source of everything interesting. Stay curious."

## Kai Voss
"Trust is the precondition of surrender. Build it slowly. Honor it completely."

## Talia Rhine
"The digital world is part of your intimate world. Navigate it with intention."

## Prof. Jun Hart
"Intimacy is a lifelong practice. What you learn now is just the beginning."

## Your Second Manifesto

Write it now. Who are you, intimately, after this course? What do you believe? What will you practice?

Compare it to your first manifesto from Level 1. How have you grown?

## Advocacy

You now know things most people don't learn explicitly. Consider:
- How will you share this knowledge appropriately?
- Who in your life might benefit from what you've learned?
- What will you do to continue your education?

Intimacy education should not be rare. You can be part of changing that.""",
        "reflection": {
            "title": "Intimacy Manifesto 2.0",
            "prompt": "Who are you now, and how do you want to love?",
            "type": "guided_reflection"
        },
        "xp_reward": 50,
        "duration_minutes": 30
    },
    {
        "id": "lesson-28",
        "course_id": "level-4-advanced-intimacy",
        "lesson_number": 28,
        "title": "Level 4 Capstone: Mastery Portfolio",
        "instructor": "All Faculty",
        "instructor_id": "prof-jun-hart",
        "description": "A video reflection. A written synthesis. An optional peer review process. Not an exam — a celebration. Evidence of transformation. The graduation moment.",
        "content": """# Mastery Portfolio

This is not an exam. This is a celebration.

## Your Portfolio

### Component 1: Video Reflection
Record yourself (for your eyes only, unless you choose to share) answering:
- What was I like at the beginning of this course?
- What do I understand now that I didn't then?
- What practices have I integrated into my life?
- What's still growing?

### Component 2: Written Synthesis
In writing, synthesize:
- Your key learnings from each level
- Your manifestos (original and updated)
- Your ongoing questions and edges

### Component 3: Forever Practice Design
Design your ongoing intimacy practice:
- What daily or weekly practices will you maintain?
- How will you continue learning?
- Who is your intimate community?
- What support do you need?

## The Credential

Completing this portfolio earns you the **Intimacy Mastery** credential.

This is not the end. This is a beginning.

## The Hedonistic Lab: Design Your Forever Practice

What will intimacy look like in your life from here forward? Not as a goal achieved, but as an ongoing practice.

---

*Welcome to The Intimacy Course. You were always ready for this.*

*Now you know it too.*""",
        "lab": {
            "title": "Design Your Forever Practice",
            "description": "Create your personal intimacy practice for the rest of your life.",
            "duration_minutes": 30,
            "type": "hedonistic_lab"
        },
        "xp_reward": 200,
        "duration_minutes": 45
    }
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
        "created_at": now
    }
    
    await db.users.insert_one(user_doc)
    
    token = create_token(user_id)
    user_response = UserResponse(**{k: v for k, v in user_doc.items() if k != "password" and k != "_id"})
    
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
        completed_labs=user.get("completed_labs", []),
        badges=user.get("badges", []),
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

@api_router.get("/courses/{course_id}/lessons")
async def get_lessons(course_id: str):
    lessons = [l for l in LESSONS_DATA if l["course_id"] == course_id]
    # Return simplified lesson data for list view
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
        "has_reflection": l.get("reflection") is not None
    } for l in lessons]

@api_router.get("/lessons/{lesson_id}")
async def get_lesson(lesson_id: str):
    for lesson in LESSONS_DATA:
        if lesson["id"] == lesson_id:
            return lesson
    raise HTTPException(status_code=404, detail="Lesson not found")

@api_router.post("/lessons/{lesson_id}/complete")
async def complete_lesson(lesson_id: str, current_user: dict = Depends(get_current_user)):
    lesson = None
    for l in LESSONS_DATA:
        if l["id"] == lesson_id:
            lesson = l
            break
    
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    user_id = current_user["id"]
    completed = current_user.get("completed_lessons", [])
    
    if lesson_id in completed:
        return {"message": "Lesson already completed", "xp_earned": 0}
    
    new_xp = current_user.get("xp", 0) + lesson["xp_reward"]
    new_level = (new_xp // 500) + 1
    completed.append(lesson_id)
    
    # Check for badge unlocks
    badges = current_user.get("badges", [])
    course_id = lesson["course_id"]
    course_lessons = [l for l in LESSONS_DATA if l["course_id"] == course_id]
    completed_course_lessons = [l for l in course_lessons if l["id"] in completed]
    
    badge_updates = []
    if len(completed_course_lessons) == len(course_lessons):
        if course_id == "level-1-self-intimacy" and "self-intimacy-sovereign" not in badges:
            badges.append("self-intimacy-sovereign")
            badge_updates.append("Self-Intimacy Sovereign")
        elif course_id == "level-2-connected-intimacy" and "connection-fluent" not in badges:
            badges.append("connection-fluent")
            badge_updates.append("Connection Fluent")
        elif course_id == "level-3-diverse-intimacy" and "diversity-explorer" not in badges:
            badges.append("diversity-explorer")
            badge_updates.append("Diversity Explorer")
        elif course_id == "level-4-advanced-intimacy" and "intimacy-master" not in badges:
            badges.append("intimacy-master")
            badge_updates.append("Intimacy Master")
    
    await db.users.update_one(
        {"id": user_id},
        {"$set": {
            "xp": new_xp,
            "level": new_level,
            "completed_lessons": completed,
            "badges": badges
        }}
    )
    
    return {
        "message": "Lesson completed!",
        "xp_earned": lesson["xp_reward"],
        "total_xp": new_xp,
        "level": new_level,
        "badges_earned": badge_updates
    }

@api_router.post("/labs/{lesson_id}/complete")
async def complete_lab(lesson_id: str, current_user: dict = Depends(get_current_user)):
    lesson = None
    for l in LESSONS_DATA:
        if l["id"] == lesson_id:
            lesson = l
            break
    
    if not lesson or not lesson.get("lab"):
        raise HTTPException(status_code=404, detail="Lab not found")
    
    user_id = current_user["id"]
    completed_labs = current_user.get("completed_labs", [])
    
    if lesson_id in completed_labs:
        return {"message": "Lab already completed", "tokens_earned": 0}
    
    completed_labs.append(lesson_id)
    tokens = current_user.get("tokens", 0) + 25
    
    await db.users.update_one(
        {"id": user_id},
        {"$set": {
            "completed_labs": completed_labs,
            "tokens": tokens
        }}
    )
    
    return {
        "message": "Lab completed!",
        "tokens_earned": 25,
        "total_tokens": tokens
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
    return {"message": "Fleshsesh Academy API", "status": "running", "version": "2.0"}

@api_router.get("/health")
async def health_check():
    return {"status": "healthy"}

# ============== STATS ==============

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
        "total_instructors": len(INSTRUCTORS_DATA)
    }

# Include the router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
