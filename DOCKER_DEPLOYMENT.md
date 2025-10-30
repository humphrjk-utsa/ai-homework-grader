# Docker Deployment Guide

## 🐳 Overview

This guide covers deploying the AI Homework Grader in Docker containers for easy portability and deployment.

---

## 📋 Prerequisites

### Required:
- Docker Desktop (Mac/Windows) or Docker Engine (Linux)
- Docker Compose v2.0+
- 16GB+ RAM recommended
- 50GB+ free disk space

### For Mac Silicon (M1/M2/M3/M4):
- macOS 12.0+
- Apple Silicon Mac (required for MLX models)

### For Other Platforms:
- Will need to use alternative models (OpenAI API, Ollama, etc.)
- MLX models only work on Apple Silicon

---

## 🚀 Quick Start

### 1. Build and Start All Services

```bash
# Build all containers
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### 2. Access the Application

- **Streamlit App:** http://localhost:8501
- **GPT-OSS Server:** http://localhost:5001
- **Qwen Server:** http://localhost:5002

### 3. Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (careful - deletes data!)
docker-compose down -v
```

---

## 🏗️ Architecture

### Container Structure:

```
┌─────────────────────────────────────────┐
│         Docker Host (Mac Studio)        │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │  Streamlit App Container           │ │
│  │  Port: 8501                        │ │
│  │  - Web Interface                   │ │
│  │  - Grading Logic                   │ │
│  │  - Database                        │ │
│  └────────────────────────────────────┘ │
│              ↓         ↓                 │
│  ┌──────────────┐  ┌──────────────┐    │
│  │ GPT-OSS      │  │ Qwen Server  │    │
│  │ Container    │  │ Container    │    │
│  │ Port: 5001   │  │ Port: 5002   │    │
│  └──────────────┘  └──────────────┘    │
│                                          │
│  Shared Network: grader-network         │
└─────────────────────────────────────────┘
```

---

## 📁 Volume Mounts

### Persistent Data:

The following directories are mounted as volumes to persist data:

```yaml
volumes:
  - ./data:/app/data                          # Student submissions
  - ./rubrics:/app/rubrics                    # Grading rubrics
  - ./sample_datasets:/app/sample_datasets    # Sample data
  - ./graded_submissions:/app/graded_submissions  # Graded work
  - ./training_data:/app/training_data        # AI training data
  - ./logs:/app/logs                          # Application logs
  - ./grading_database.db:/app/grading_database.db  # SQLite DB
```

**Benefits:**
- Data persists across container restarts
- Easy backup (just backup these directories)
- Can edit files on host, changes reflect in container

---

## 🔧 Configuration

### Environment Variables

Edit `docker-compose.yml` to configure:

```yaml
environment:
  # Model settings
  - MODEL_NAME=lmstudio-community/gpt-oss-120b-MLX-8bit
  - MAX_TOKENS=800
  - TEMPERATURE=0.3
  
  # Server settings
  - FLASK_ENV=production
  - STREAMLIT_SERVER_PORT=8501
```

### Distributed Config

Edit `distributed_config.json` for model parameters:

```json
{
  "mac_studio_1": {
    "ip": "gpt-oss-server",  // Use container name
    "port": 5001,
    "max_tokens": 800
  },
  "mac_studio_2": {
    "ip": "qwen-server",     // Use container name
    "port": 5002,
    "max_tokens": 1200
  }
}
```

---

## 🛠️ Development Workflow

### Local Development with Docker

```bash
# Start services in development mode
docker-compose up

# Make code changes on host
# Container auto-reloads (if configured)

# View logs
docker-compose logs -f app

# Restart specific service
docker-compose restart app

# Rebuild after dependency changes
docker-compose build app
docker-compose up -d app
```

### Debugging

```bash
# Enter container shell
docker exec -it ai-homework-grader bash

# Check container logs
docker logs ai-homework-grader

# Check server health
curl http://localhost:5001/health
curl http://localhost:5002/health

# Monitor resource usage
docker stats
```

---

## 📦 Building for Production

### Optimized Build

```bash
# Build with no cache (clean build)
docker-compose build --no-cache

# Build specific service
docker-compose build app

# Tag for registry
docker tag ai-homework-grader:latest myregistry/ai-homework-grader:v1.0

# Push to registry
docker push myregistry/ai-homework-grader:v1.0
```

### Multi-Stage Build (Future Optimization)

```dockerfile
# Build stage
FROM python:3.9-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.9-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
CMD ["streamlit", "run", "app.py"]
```

---

## 🔒 Security Considerations

### Best Practices:

1. **Don't expose ports publicly** - Use reverse proxy (nginx)
2. **Use secrets management** - Don't hardcode credentials
3. **Run as non-root user** - Add to Dockerfile:
   ```dockerfile
   RUN useradd -m -u 1000 grader
   USER grader
   ```
4. **Scan images** - Use `docker scan` or Trivy
5. **Keep images updated** - Regularly rebuild with latest base images

### Environment Secrets:

```bash
# Use .env file (don't commit!)
echo "DB_PASSWORD=secret123" > .env

# Reference in docker-compose.yml
environment:
  - DB_PASSWORD=${DB_PASSWORD}
```

---

## 🌐 Deployment Options

### Option 1: Single Mac Studio (Current)

```bash
# Run all containers on one machine
docker-compose up -d
```

**Pros:** Simple, all-in-one
**Cons:** Resource intensive

### Option 2: Distributed Deployment

```yaml
# docker-compose.mac1.yml (Mac Studio 1)
services:
  app:
    # ... app config
  gpt-oss-server:
    # ... GPT-OSS config

# docker-compose.mac2.yml (Mac Studio 2)
services:
  qwen-server:
    # ... Qwen config
```

**Pros:** Better resource distribution
**Cons:** More complex networking

### Option 3: Cloud Deployment (Non-MLX)

For cloud deployment, replace MLX models with:
- OpenAI API
- Anthropic Claude API
- Ollama with CPU models
- HuggingFace Inference API

---

## 📊 Monitoring

### Health Checks

```bash
# Check all services
docker-compose ps

# Check specific service health
docker inspect --format='{{.State.Health.Status}}' ai-homework-grader

# View health check logs
docker inspect --format='{{range .State.Health.Log}}{{.Output}}{{end}}' ai-homework-grader
```

### Resource Monitoring

```bash
# Real-time stats
docker stats

# Specific container
docker stats ai-homework-grader

# Export metrics
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

---

## 🔄 Backup and Restore

### Backup

```bash
# Backup volumes
docker run --rm \
  -v ai-homework-grader_grading-data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/grading-data-backup.tar.gz /data

# Backup database
docker exec ai-homework-grader \
  sqlite3 /app/grading_database.db ".backup /app/backup.db"
docker cp ai-homework-grader:/app/backup.db ./backup.db
```

### Restore

```bash
# Restore volumes
docker run --rm \
  -v ai-homework-grader_grading-data:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/grading-data-backup.tar.gz -C /

# Restore database
docker cp ./backup.db ai-homework-grader:/app/grading_database.db
```

---

## 🐛 Troubleshooting

### Common Issues:

#### 1. Port Already in Use
```bash
# Find process using port
lsof -i :8501

# Kill process
kill -9 <PID>

# Or change port in docker-compose.yml
ports:
  - "8502:8501"  # Use different host port
```

#### 2. Container Won't Start
```bash
# Check logs
docker-compose logs app

# Check for errors
docker-compose ps

# Rebuild
docker-compose build --no-cache app
docker-compose up -d app
```

#### 3. MLX Models Not Working
```bash
# MLX only works on Apple Silicon
# Check architecture
uname -m  # Should show "arm64"

# For non-Mac, use alternative models
# Edit docker-compose.yml to use OpenAI API instead
```

#### 4. Out of Memory
```bash
# Check memory usage
docker stats

# Increase Docker memory limit
# Docker Desktop > Settings > Resources > Memory

# Or limit container memory
docker-compose.yml:
  services:
    app:
      mem_limit: 8g
```

---

## 📚 Additional Resources

### Docker Commands Cheat Sheet:

```bash
# Build
docker-compose build
docker-compose build --no-cache

# Start/Stop
docker-compose up -d
docker-compose down
docker-compose restart

# Logs
docker-compose logs -f
docker-compose logs -f app

# Shell Access
docker exec -it ai-homework-grader bash

# Clean Up
docker system prune -a
docker volume prune
```

### Useful Links:
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [MLX Documentation](https://ml-explore.github.io/mlx/)
- [Streamlit Docker Guide](https://docs.streamlit.io/knowledge-base/tutorials/deploy/docker)

---

## 🎯 Next Steps

1. **Test locally:** `docker-compose up`
2. **Verify services:** Check all health endpoints
3. **Grade test submission:** Upload and grade a sample
4. **Monitor performance:** Check logs and metrics
5. **Optimize:** Adjust resources as needed
6. **Deploy:** Push to production when ready

---

## ⚠️ Important Notes

### MLX Limitation:
- MLX models **only work on Apple Silicon Macs**
- For other platforms, you'll need to:
  - Use OpenAI API
  - Use Ollama with CPU models
  - Use cloud-based inference APIs

### Performance:
- Docker adds ~5-10% overhead
- For maximum performance, run natively
- Use Docker for portability and easy deployment

### Data Persistence:
- Always use volumes for important data
- Backup regularly
- Test restore procedures

---

## 📝 Summary

**Docker deployment provides:**
- ✅ Easy setup and deployment
- ✅ Consistent environment
- ✅ Easy scaling and updates
- ✅ Isolated dependencies
- ✅ Simple backup/restore

**Trade-offs:**
- ❌ Slight performance overhead
- ❌ MLX requires Apple Silicon
- ❌ More complex than native deployment

**Best for:**
- Development environments
- Testing and staging
- Cloud deployment (with alternative models)
- Easy distribution to other users
