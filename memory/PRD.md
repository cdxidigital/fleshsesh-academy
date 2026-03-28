# Fleshsesh Academy - Product Requirements Document

## Original Problem Statement
Build Fleshsesh Academy eCampus - an AI-powered intimacy education platform with comprehensive courses, 8 AI faculty members with unique personalities, age verification gateway, AI student advisor, A-Z encyclopedia, student journey map, and real AI chat with faculty.

## What's Been Implemented

### Core Platform (Completed - March 2026)
- **Age Verification Gateway** - 18+ verification with localStorage persistence
- **User Authentication** - JWT-based login/register with progress tracking
- **Course Dashboard** - XP, level, tokens, subscription status display
- **Navigation** - Header with transparent PNG logos, nav links, auth controls

### Curriculum (Completed - March 2026)
- **4 Mastery Levels**: Self-Intimacy → Connected Intimacy → Diverse Intimacy → Advanced Intimacy
- **28 Transformative Lessons** (7 per level) with full content
- **14 Hedonistic Labs** - hands-on practice exercises
- **~12.5 hours** of total content

### AI Faculty (Completed - March 2026)
8 unique instructors with deep profiles:
1. Dr. Nova Vale - Sexual Physiology & Body Science
2. Coach Mira Sol - Self-Love, Shame Resilience & Somatic Practice
3. Prof. Arden Moss - Consent, Communication & Relational Ethics
4. Dr. Elise Hart - Shared Pleasure & Partnered Practice
5. Dr. Sera Quinn - Identity, Diversity & Intersectional Intimacy
6. Kai Voss - Kink, Power Dynamics & Edge Exploration
7. Talia Rhine - Digital Intimacy, Ethics & Online Safety
8. Prof. Jun Hart - Media Literacy, Lifelong Intimacy & Mastery

### Real AI Faculty Chat (NEW - March 2026)
- **Integration**: Uses emergentintegrations library with GPT-4o model
- **Personalized Responses**: Each instructor responds in character based on their personality profile
- **Chat Storage**: Messages stored in MongoDB with full session management
- **Features**:
  - Chat history panel
  - New chat button
  - Delete chat sessions
  - Typing indicators
  - Message persistence
- **Route**: `/chat/:instructorId`

### A-Z Encyclopedia (Completed - March 2026)
- Dedicated `/encyclopedia` page with category filtering, search, entry details, faculty insights, bookmarking

### Student Journey Map (Completed - March 2026)
- Dedicated `/journey` page with progress visualization, level tracking, badges

### AI Student Advisor (Completed - March 2026)
- "Sage" chat widget for platform navigation help

### Branding (Updated - March 2026)
- Transparent PNG logos deployed:
  - Full logo: `3848ji5y_...transparent.png`
  - Icon logo: `d0c4rw6h_...transparent.png`

## Technical Stack
- **Backend**: FastAPI + MongoDB
- **Frontend**: React + TailwindCSS + shadcn/ui
- **Auth**: JWT with bcrypt password hashing
- **LLM Integration**: emergentintegrations library with GPT-4o
- **Deployment**: Kubernetes (preview environment)

## API Endpoints
- `/api/auth/register`, `/api/auth/login`, `/api/auth/me`
- `/api/courses`, `/api/courses/{id}`, `/api/courses/{id}/lessons`
- `/api/instructors`, `/api/instructors/{id}`
- `/api/encyclopedia`, `/api/encyclopedia/{id}`, `/api/encyclopedia/{id}/bookmark`
- `/api/labs`, `/api/labs/{id}/complete`
- `/api/chat/faculty` (POST) - Send message to AI faculty
- `/api/chat/sessions` - Get/list chat sessions
- `/api/chat/sessions/{id}` - Get/delete specific session
- `/api/stats`, `/api/health`

## Subscription Tiers
- **Free** ($0) - Level 1 access (7 lessons)
- **Premium** ($24.99/mo) - All 28 lessons, 14 labs, AI Faculty chat
- **Elite** ($64.99/mo) - Premium + coaching, 1-on-1 AI sessions, A-Z Encyclopedia

## Prioritized Backlog

### P0 (Critical for Launch)
- [ ] Stripe payment integration for subscription tiers
- [ ] Email verification for registration
- [ ] Interactive labs with guided exercises

### P1 (High Priority)
- [ ] Community forums and anonymous Q&A
- [ ] Certificate generation on level completion
- [ ] Mobile responsiveness optimization

### P2 (Medium Priority)
- [ ] Interactive simulations/role-play
- [ ] Partner/couples account linking
- [ ] Push notifications for streaks

### P3 (Future)
- [ ] Video content integration
- [ ] Live group coaching sessions
- [ ] API for third-party integrations

## Files Reference
- `/app/backend/server.py` - Main FastAPI application with chat endpoints
- `/app/frontend/src/pages/FacultyChat.js` - AI Faculty chat page
- `/app/frontend/src/pages/Encyclopedia.js` - Encyclopedia page
- `/app/frontend/src/pages/JourneyMap.js` - Journey map page
- `/app/frontend/src/components/AIAdvisor.js` - Sage chat widget

## Test Reports
- `/app/test_reports/iteration_5.json` - Latest comprehensive test (all pass)
- `/app/backend/tests/test_api_endpoints.py` - Backend API test suite
- `/app/backend/tests/test_faculty_chat.py` - Faculty chat test suite
