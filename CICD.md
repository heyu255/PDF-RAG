# CI/CD Setup Guide

This project uses GitHub Actions for Continuous Integration and Continuous Deployment.

## CI Pipeline (`.github/workflows/ci.yml`)

Runs on every push and pull request:

1. **Backend Tests**
   - Installs Python dependencies
   - Runs linting (flake8)
   - Tests imports

2. **Frontend Tests**
   - Installs Node.js dependencies
   - Runs ESLint
   - Builds the application

3. **Docker Build**
   - Builds both backend and frontend Docker images
   - Uses build cache for faster builds

## CD Pipeline (`.github/workflows/cd.yml`)

Runs on pushes to `main` branch:

1. **Deploy Backend to Render**
   - Render auto-deploys on push (no action needed)
   - Or can trigger via Render API

2. **Deploy Frontend to Vercel**
   - Automatically deploys to Vercel
   - Requires Vercel secrets configured

## Required GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions

### For CI (Testing):
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_SERVICE_ROLE_KEY` - Your Supabase service role key

### For CD (Deployment):
- `VERCEL_TOKEN` - Get from Vercel Dashboard → Settings → Tokens
- `VERCEL_ORG_ID` - Get from Vercel Dashboard → Settings → General
- `VERCEL_PROJECT_ID` - Get from your Vercel project settings

### Optional (for Render API):
- `RENDER_API_KEY` - If you want to trigger Render deployments via API
- `RENDER_SERVICE_ID` - Your Render service ID

## How to Get Vercel Secrets

1. **VERCEL_TOKEN**:
   - Go to https://vercel.com/account/tokens
   - Create a new token
   - Copy the token

2. **VERCEL_ORG_ID**:
   - Go to Vercel Dashboard → Settings → General
   - Copy "Team ID" (this is your org ID)

3. **VERCEL_PROJECT_ID**:
   - Go to your project in Vercel
   - Settings → General
   - Copy "Project ID"

## Workflow Status

Check workflow status:
- Go to your GitHub repository
- Click "Actions" tab
- See all workflow runs and their status

## Manual Deployment

You can also manually trigger deployments:

1. Go to Actions tab
2. Select "CD Pipeline"
3. Click "Run workflow"
4. Choose branch and click "Run workflow"

## Troubleshooting

### Workflow Fails
- Check the Actions tab for error logs
- Verify all secrets are set correctly
- Ensure branch names match (`main` for CD)

### Vercel Deployment Fails
- Verify VERCEL_TOKEN is valid
- Check VERCEL_ORG_ID and VERCEL_PROJECT_ID are correct
- Ensure Vercel project is linked to GitHub

### Render Deployment
- Render auto-deploys on push, no GitHub Action needed
- If you want API-triggered deploys, set RENDER_API_KEY and RENDER_SERVICE_ID

