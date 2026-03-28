# Fleshsesh Academy - Product Requirements Document

## Original Problem Statement
Build Fleshsesh Academy eCampus - an AI-powered intimacy education platform with comprehensive courses based on "The Intimacy Course" curriculum.

## What's Been Implemented (Jan 2026)

### Curriculum (from Notion Doc)
- **4 Mastery Levels**: Self-Intimacy → Connected Intimacy → Diverse Intimacy → Advanced Intimacy
- **28 Transformative Lessons** (7 per level)
- **12 Hedonistic Labs** - hands-on practice exercises
- **~12.5 hours** of content
- **Badges**: Self-Intimacy Sovereign, Connection Fluent, Diversity Explorer, Intimacy Master

### AI Faculty (8 Instructors)
1. Dr. Nova Vale - Sexual Physiology & Body Science
2. Coach Mira Sol - Self-Love, Shame Resilience & Somatic Practice
3. Prof. Arden Moss - Consent, Communication & Relational Ethics
4. Dr. Elise Hart - Shared Pleasure & Partnered Practice
5. Dr. Sera Quinn - Identity, Diversity & Intersectional Intimacy
6. Kai Voss - Kink, Power Dynamics & Edge Exploration
7. Talia Rhine - Digital Intimacy, Ethics & Online Safety
8. Prof. Jun Hart - Media Literacy, Lifelong Intimacy & Mastery

### Technical Implementation
- **Backend**: FastAPI + MongoDB with full CRUD, auth (JWT), progress tracking
- **Frontend**: React with enhanced UI/UX (glass morphism, animations)
- **Features**: Age verification (18+), AI Advisor (Sage), XP/badges, lesson completion

### Subscription Tiers
- Free ($0) - Level 1 access (7 lessons)
- Premium ($24.99/mo) - All content (28 lessons)
- Elite ($64.99/mo) - Premium + coaching + encyclopedia

## Prioritized Backlog

### P0 (Critical for Launch)
- [ ] Payment integration (Stripe)
- [ ] AI Faculty chat (LLM integration)
- [ ] Email verification

### P1 (High Priority)
- [ ] A-Z Encyclopedia integration
- [ ] Community forums
- [ ] Certificate generation

### P2 (Medium Priority)
- [ ] Interactive simulations
- [ ] Partner/couples accounts
- [ ] Mobile optimization

## Next Tasks
1. Integrate Stripe for subscription payments
2. Add real AI chat with faculty using LLM
3. Build A-Z Encyclopedia module
4. Add community features
