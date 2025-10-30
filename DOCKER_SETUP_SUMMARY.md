# Docker Setup - Complete

## ✅ Files Created

### Core Docker Files:
1. **`Dockerfile`** - Main application container
2. **`Dockerfile.gpt-oss`** - GPT-OSS server container
3. **`Dockerfile.qwen`** - Qwen server container
4. **`docker-compose.yml`** - Orchestrates all services
5. **`.dockerignore`** - Excludes unnecessary files from build

### Helper Scripts:
6. **`docker-start.sh`** - Quick start script
7. **`DOCKER_DEPLOYMENT.md`** - Complete deployment guide

---

## 🚀 Quick Start

### Option 1: Using the Start Script (Easiest)
```bash
./docker-start.sh
```

### Option 2: Manual Commands
```bash
# Build containers
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

---

## 📊 What Gets Deployed

### Three Containers:

1. **Streamlit App** (Port 8501)
   - Web interface
   - Grading logic
   - Database management

2. **GPT-OSS Server** (Port 5001)
   - Feedback generation
   - Mac Studio 1 model

3. **Qwen Server** (Port 5002)
   - Code analysis
   - Mac Studio 2 model

### Persistent Data (Volumes):
- `./data` - Student submissions
- `./rubrics` - Grading rubrics
- `./sample_datasets` - Sample data
- `./graded_submissions` - Graded work
- `./training_data` - AI training data
- `./logs` - Application logs
- `./grading_database.db` - SQLite database

---

## ⚠️ Important Notes

### MLX Models (Apple Silicon Only):
The current setup uses MLX models which **only work on Apple Silicon Macs** (M1/M2/M3/M4).

**For non-Mac deployment:**
- Replace MLX models with OpenAI API
- Use Ollama with CPU models
- Use cloud-based inference APIs

### Current Branch:
You're on the **Test** branch. This Docker setup is isolated and won't affect your working system.

---

## 🔧 Configuration

### Before First Run:

1. **Check distributed_config.json:**
   ```json
   {
     "mac_studio_1": {
       "ip": "gpt-oss-server",  // Use container name
       "port": 5001
     },
     "mac_studio_2": {
       "ip": "qwen-server",     // Use container name
       "port": 5002
     }
   }
   ```

2. **Verify requirements.txt** has all dependencies

3. **Ensure data directories exist:**
   ```bash
   mkdir -p data/raw data/processed rubrics sample_datasets \
            graded_submissions training_data logs
   ```

---

## 📝 Common Commands

### Start/Stop:
```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Restart
docker-compose restart

# Stop and remove volumes (careful!)
docker-compose down -v
```

### Logs:
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f app
docker-compose logs -f gpt-oss-server
docker-compose logs -f qwen-server
```

### Shell Access:
```bash
# Enter app container
docker exec -it ai-homework-grader bash

# Enter server container
docker exec -it gpt-oss-server bash
```

### Health Checks:
```bash
# Check all services
docker-compose ps

# Check specific endpoints
curl http://localhost:8501/_stcore/health
curl http://localhost:5001/health
curl http://localhost:5002/health
```

---

## 🎯 Benefits of Docker Deployment

### Advantages:
- ✅ **Portable** - Run anywhere Docker runs
- ✅ **Consistent** - Same environment everywhere
- ✅ **Isolated** - Doesn't affect host system
- ✅ **Easy Updates** - Rebuild and redeploy
- ✅ **Scalable** - Easy to add more services
- ✅ **Backup Friendly** - Just backup volumes

### Trade-offs:
- ❌ **Performance** - 5-10% overhead vs native
- ❌ **Complexity** - More moving parts
- ❌ **MLX Limitation** - Apple Silicon only
- ❌ **Resource Usage** - Each container uses memory

---

## 🔄 Development Workflow

### Making Changes:

1. **Edit code on host** (changes reflect in container via volumes)
2. **Restart service** if needed:
   ```bash
   docker-compose restart app
   ```
3. **Rebuild** if dependencies changed:
   ```bash
   docker-compose build app
   docker-compose up -d app
   ```

### Testing:
```bash
# Run in foreground to see logs
docker-compose up

# Make changes, test, iterate

# When satisfied, run in background
docker-compose up -d
```

---

## 🐛 Troubleshooting

### Container Won't Start:
```bash
# Check logs
docker-compose logs app

# Rebuild
docker-compose build --no-cache app
docker-compose up -d app
```

### Port Conflicts:
```bash
# Find what's using the port
lsof -i :8501

# Kill the process or change port in docker-compose.yml
```

### Out of Memory:
```bash
# Check usage
docker stats

# Increase Docker memory
# Docker Desktop > Settings > Resources > Memory
```

### Models Not Loading:
```bash
# Check server logs
docker-compose logs gpt-oss-server
docker-compose logs qwen-server

# Verify MLX is available (Apple Silicon only)
docker exec -it gpt-oss-server python -c "import mlx; print('MLX OK')"
```

---

## 📚 Next Steps

### 1. Test the Setup:
```bash
./docker-start.sh
```

### 2. Verify Services:
- Open http://localhost:8501
- Check server health endpoints
- Upload a test submission

### 3. Monitor Performance:
```bash
docker stats
docker-compose logs -f
```

### 4. Customize:
- Edit `docker-compose.yml` for your needs
- Adjust resource limits
- Configure environment variables

### 5. Deploy:
- Test thoroughly on Test branch
- Merge to master when ready
- Deploy to production

---

## 🎓 Learning Resources

- **Docker Basics:** https://docs.docker.com/get-started/
- **Docker Compose:** https://docs.docker.com/compose/
- **Streamlit + Docker:** https://docs.streamlit.io/knowledge-base/tutorials/deploy/docker
- **MLX:** https://ml-explore.github.io/mlx/

---

## ✨ Summary

You now have a complete Docker setup for the AI Homework Grader:

- ✅ Three containerized services
- ✅ Persistent data volumes
- ✅ Easy start/stop scripts
- ✅ Comprehensive documentation
- ✅ Health checks and monitoring
- ✅ Development-friendly workflow

**To get started:**
```bash
./docker-start.sh
```

**To stop:**
```bash
docker-compose down
```

The system is isolated in Docker and won't affect your current working setup!
