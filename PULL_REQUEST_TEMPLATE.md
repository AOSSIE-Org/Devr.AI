# Fix User Profile Data & Add Editable Profile Page

## Description

Fixes the issue where user profile information was incorrect or missing after signup and adds a fully functional editable profile page.

## What Changed

### Backend
- ✅ New API endpoints: `GET /v1/users/me` and `PUT /v1/users/me` 
- ✅ Database trigger to auto-sync user display_name from signup metadata
- ✅ User profile table with RLS security policies

### Frontend
- ✅ Profile page now fetches real data from backend
- ✅ Full edit mode with cancel/save functionality
- ✅ Email field is read-only (non-editable)
- ✅ Editable: display name, bio, location
- ✅ Shows platform integrations: GitHub, Discord, Slack

## For Maintainers: Required Setup Steps

### 1. Apply Database Migration (REQUIRED)
Run this SQL in your **Supabase Dashboard** → SQL Editor:

```sql
-- File: backend/database/02_create_users_table.sql
-- Copy entire file and run in Supabase SQL editor
```

This creates:
- `public.users` table with profile fields
- Auto-sync trigger for new signups
- Row Level Security policies
- Database indexes

### 2. Restart Backend
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

### 3. Test
1. Go to `/signup` and create account
2. Verify display_name shows in `/profile`
3. Click "Edit Profile" and update fields
4. Verify email is read-only
5. Click "Save Changes" - should show success toast

## Files Changed
- `backend/app/api/v1/users.py` (NEW)
- `backend/database/02_create_users_table.sql` (NEW)
- `backend/app/api/router.py` (modified)
- `frontend/src/lib/api.ts` (modified)
- `frontend/src/components/pages/ProfilePage.tsx` (rewritten)

## Issue Resolution
✅ User profile data correctly captured after signup  
✅ Editable profile page with real data  
✅ Email visible but non-editable  
✅ Profile changes persist  
✅ Proper error handling & loading states

## Security
- JWT authentication required
- Row Level Security on database
- Email field non-editable
- Input validation both frontend & backend

## Merge Checklist
- [ ] Run database migration SQL
- [ ] Verify backend starts without errors
- [ ] Test signup → profile flow
- [ ] Verify profile edit saves data

---
**Note:** Database migration is required before this feature works. Run the SQL file in Supabase before deploying.
