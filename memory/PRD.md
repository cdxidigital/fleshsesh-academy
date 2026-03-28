# Fleshsesh Academy - Product Requirements Document

## Original Problem Statement
Build Fleshsesh Academy eCampus - an AI-powered intimacy education platform with comprehensive courses based on "The Intimacy Course" curriculum. Features include 4 mastery levels, 28 lessons, 14 hedonistic labs, 8 AI faculty members, age verification gateway, AI student advisor, A-Z encyclopedia, and student journey map.

## What's Been Implemented

### Core Platform (Completed - March 2026)
- **Age Verification Gateway** - 18+ verification with localStorage persistence
- **User Authentication** - JWT-based login/register with progress tracking
- **Course Dashboard** - XP, level, tokens, subscription status display
- **Navigation** - Header with logo, nav links, auth controls

### Curriculum (Completed - March 2026)
- **4 Mastery Levels**: Self-Intimacy → Connected Intimacy → Diverse Intimacy → Advanced Intimacy
- **28 Transformative Lessons** (7 per level) with full content
- **14 Hedonistic Labs** - hands-on practice exercises
- **~12.5 hours** of total content
- **Badges**: Self-Intimacy Sovereign, Connection Fluent, Diversity Explorer, Intimacy Master

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

### A-Z Encyclopedia (Completed - March 2026)
- Dedicated `/encyclopedia` page with:
  - Category filtering (Anatomy, Communication, Pleasure, Kink, Relational)
  - Search functionality
  - Entry detail view with definition, context, science, practice, safety
  - Faculty insights per entry
  - Bookmark functionality (authenticated)
  - Difficulty levels (beginner/intermediate/advanced)

### Student Journey Map (Completed - March 2026)
- Dedicated `/journey` page with:
  - Overall progress visualization
  - Level-by-level progress tracking
  - Lesson completion grid
  - Badge display and unlock status
  - Course navigation

### AI Student Advisor (Completed - March 2026)
- "Sage" chat widget in bottom-right corner
- Quick replies for common questions
- Context-aware responses about courses, faculty, pricing, XP
- Minimizable/closeable interface

### Branding (Updated - March 2026)
- New logos deployed:
  - Full logo: "Fleshsesh Academy" with lips
  - Icon logo: "F" with lips (for header mobile)
- Used across: Age verification, Header, Footer, Landing hero

## Technical Stack
- **Backend**: FastAPI + MongoDB
- **Frontend**: React + TailwindCSS + shadcn/ui
- **Auth**: JWT with bcrypt password hashing
- **Deployment**: Kubernetes (preview environment)

## API Endpoints
- `/api/auth/register`, `/api/auth/login`, `/api/auth/me`
- `/api/courses`, `/api/courses/{id}`, `/api/courses/{id}/lessons`
- `/api/lessons/{id}`, `/api/lessons/{id}/complete`
- `/api/instructors`, `/api/instructors/{id}`
- `/api/encyclopedia`, `/api/encyclopedia/{id}`, `/api/encyclopedia/{id}/bookmark`
- `/api/labs`, `/api/labs/{id}/complete`
- `/api/stats`, `/api/health`

## Subscription Tiers
- **Free** ($0) - Level 1 access (7 lessons)
- **Premium** ($24.99/mo) - All 28 lessons, 14 labs, AI Faculty chat
- **Elite** ($64.99/mo) - Premium + coaching, 1-on-1 AI sessions, A-Z Encyclopedia

## Prioritized Backlog

### P0 (Critical for Launch)
- [ ] Payment integration (Stripe) for subscription tiers
- [ ] Real AI chat with faculty using LLM integration
- [ ] Email verification for registration

### P1 (High Priority)
- [ ] Interactive labs with guided exercises
- [ ] Community forums and anonymous Q&A
- [ ] Certificate generation on level completion
- [ ] Mobile responsiveness optimization

### P2 (Medium Priority)
- [ ] Interactive simulations/role-play
- [ ] Partner/couples account linking
- [ ] Push notifications for streaks
- [ ] Dark/light theme toggle

### P3 (Future)
- [ ] Video content integration
- [ ] Live group coaching sessions
- [ ] Peer review for mastery portfolio
- [ ] API for third-party integrations

## Files Reference
- `/app/backend/server.py` - Main FastAPI application
- `/app/frontend/src/App.js` - React routing
- `/app/frontend/src/pages/Encyclopedia.js` - Encyclopedia page
- `/app/frontend/src/pages/JourneyMap.js` - Journey map page
- `/app/frontend/src/components/AIAdvisor.js` - Chat widget
- `/app/frontend/src/components/Header.js` - Navigation header
- `/app/frontend/src/components/Footer.js` - Site footer
- `/app/frontend/src/components/AgeVerification.js` - Age gate

## Test Reports
- `/app/test_reports/iteration_4.json` - Latest comprehensive test (all pass)
- `/app/backend/tests/test_api_endpoints.py` - Backend test suite
