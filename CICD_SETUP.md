# CI/CD Setup Guide

Complete guide to set up fully functional CI/CD for this project.

## Required GitHub Secrets

Add these secrets in: **Repository → Settings → Secrets and variables → Actions**

### Backend Secrets (Required for CI)

| Secret Name | Where to Find | Required For |
|------------|---------------|--------------|
| `SUPABASE_URL` | Supabase Dashboard → Settings → API → Project URL | Backend tests |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase Dashboard → Settings → API → service_role key | Backend tests |
| `OPENAI_API_KEY` | OpenAI Platform → API Keys | Backend tests (optional) |
| `PINECONE_API_KEY` | Pinecone Dashboard → API Keys | Backend tests (optional) |
| `PINECONE_INDEX_NAME` | Pinecone Dashboard → Your Index Name | Backend tests (optional) |

### Frontend Secrets (Required for CD)

| Secret Name | Where to Find | Required For |
|------------|---------------|--------------|
| `VERCEL_TOKEN` | Vercel Dashboard → Settings → Tokens → Create Token | Vercel deployment |
| `VERCEL_ORG_ID` | Vercel Dashboard → Settings → General → Team ID | Vercel deployment |
| `VERCEL_PROJECT_ID` | Vercel Project → Settings → General → Project ID | Vercel deployment |
| `NEXT_PUBLIC_API_BASE_URL` | Your backend URL (e.g., `https://your-backend.onrender.com`) | Frontend build |

---

## Step-by-Step: Getting Vercel Secrets

### 1. Get VERCEL_TOKEN

1. Go to https://vercel.com/account/tokens
2. Click **"Create Token"**
3. Name it: `GitHub Actions Deployment`
4. Select scope: **Full Account** (or your team)
5. Click **"Create"**
6. **Copy the token immediately** (you won't see it again!)
7. Add to GitHub Secrets as `VERCEL_TOKEN`

### 2. Get VERCEL_ORG_ID

1. Go to https://vercel.com/dashboard
2. Click your **Team/Account name** (top left)
3. Go to **Settings → General**
4. Find **"Team ID"** (looks like: `team_xxxxxxxxxxxxx`)
5. Copy it
6. Add to GitHub Secrets as `VERCEL_ORG_ID`

### 3. Get VERCEL_PROJECT_ID

1. Go to your Vercel project dashboard
2. Click **Settings** (top menu)
3. Go to **General** tab
4. Find **"Project ID"** (looks like: `prj_xxxxxxxxxxxxx`)
5. Copy it
6. Add to GitHub Secrets as `VERCEL_PROJECT_ID`

### 4. Get NEXT_PUBLIC_API_BASE_URL

This should be your **backend URL** from Render:
- Example: `https://pdf-rag-backend.onrender.com`
- Add to GitHub Secrets as `NEXT_PUBLIC_API_BASE_URL`

---

## Step-by-Step: Getting Supabase Secrets

### 1. Get SUPABASE_URL

1. Go to https://supabase.com/dashboard
2. Select your project
3. Go to **Settings → API**
4. Find **"Project URL"** (looks like: `https://xxxxx.supabase.co`)
5. Copy it
6. Add to GitHub Secrets as `SUPABASE_URL`

### 2. Get SUPABASE_SERVICE_ROLE_KEY

1. Same page (Settings → API)
2. Find **"service_role"** key (under "Project API keys")
3. Click **"Reveal"** or **"Copy"**
4. **⚠️ This is a secret key - keep it safe!**
5. Add to GitHub Secrets as `SUPABASE_SERVICE_ROLE_KEY`

---

## Verify Secrets Are Added

1. Go to your GitHub repo
2. **Settings → Secrets and variables → Actions**
3. You should see all secrets listed

---

## Test the CI/CD

### Test CI (on any branch):
```bash
git push
```
- Go to **Actions** tab
- Should see "CI Pipeline" running
- Should pass ✅

### Test CD (on main branch):
```bash
git checkout main
git push
```
- Go to **Actions** tab
- Should see "CD Pipeline" running
- Should deploy to Vercel ✅

---

## Troubleshooting

### CI Fails
- Check that `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are set
- Check the Actions logs for specific errors

### CD Fails
- Verify all 3 Vercel secrets are set correctly
- Check that `VERCEL_PROJECT_ID` matches your actual project
- Verify `NEXT_PUBLIC_API_BASE_URL` is your backend URL

### Vercel Deployment Not Working
- Make sure your Vercel project is linked to the GitHub repo
- Verify the token has correct permissions
- Check Vercel dashboard for deployment status

---

## What Happens When You Push

### On Any Branch:
1. ✅ **CI Pipeline** runs:
   - Tests backend imports
   - Tests frontend build
   - Builds Docker images

### On Main Branch:
1. ✅ **CI Pipeline** runs (same as above)
2. ✅ **CD Pipeline** runs:
   - Backend: Render auto-deploys (via webhook)
   - Frontend: Deploys to Vercel automatically

---

## Quick Checklist

- [ ] `SUPABASE_URL` added to GitHub Secrets
- [ ] `SUPABASE_SERVICE_ROLE_KEY` added to GitHub Secrets
- [ ] `VERCEL_TOKEN` added to GitHub Secrets
- [ ] `VERCEL_ORG_ID` added to GitHub Secrets
- [ ] `VERCEL_PROJECT_ID` added to GitHub Secrets
- [ ] `NEXT_PUBLIC_API_BASE_URL` added to GitHub Secrets (your backend URL)
- [ ] Pushed code to test CI/CD
- [ ] Verified Actions tab shows successful runs

Once all secrets are added, your CI/CD will be fully functional! 🚀

