# Docker Setup Guide

This project is containerized using Docker and Docker Compose.

## Prerequisites

- Docker Desktop installed
- Docker Compose installed (comes with Docker Desktop)

## Quick Start

### 1. Create Environment File

Create a `.env` file in the root directory:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
OPENAI_API_KEY=your_openai_key
PINECONE_API_KEY=your_pinecone_key
PINECONE_INDEX_NAME=your_pinecone_index
ALLOWED_ORIGINS=http://localhost:3000
```

### 2. Run with Docker Compose

```bash
docker-compose up --build
```

This will:
- Build both backend and frontend images
- Start both containers
- Backend available at: http://localhost:8000
- Frontend available at: http://localhost:3000

### 3. Run in Detached Mode

```bash
docker-compose up -d
```

### 4. View Logs

```bash
docker-compose logs -f
```

### 5. Stop Containers

```bash
docker-compose down
```

## Individual Container Commands

### Build Backend Only

```bash
cd backend
docker build -t pdf-rag-backend .
docker run -p 8000:8000 --env-file ../.env pdf-rag-backend
```

### Build Frontend Only

```bash
cd frontend
docker build -t pdf-rag-frontend .
docker run -p 3000:3000 -e NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 pdf-rag-frontend
```

## Production Deployment

For production, you can push images to a container registry:

```bash
# Tag images
docker tag pdf-rag-backend your-registry/pdf-rag-backend:latest
docker tag pdf-rag-frontend your-registry/pdf-rag-frontend:latest

# Push to registry
docker push your-registry/pdf-rag-backend:latest
docker push your-registry/pdf-rag-frontend:latest
```

## Troubleshooting

### Port Already in Use
If ports 3000 or 8000 are already in use, modify `docker-compose.yml`:

```yaml
ports:
  - "3001:3000"  # Change host port
```

### Environment Variables Not Loading
Make sure your `.env` file is in the root directory and variables are correctly named.

### Build Fails
- Check Docker is running
- Ensure you have enough disk space
- Try `docker system prune` to clean up

