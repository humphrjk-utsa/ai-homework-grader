#!/bin/bash
# Quick start script for Docker deployment

set -e

echo "🐳 AI Homework Grader - Docker Deployment"
echo "=========================================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running"
    echo "   Please start Docker Desktop and try again"
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: docker-compose not found"
    echo "   Please install Docker Compose"
    exit 1
fi

echo "✅ Docker Compose is available"
echo ""

# Build containers
echo "🔨 Building containers..."
docker-compose build

echo ""
echo "🚀 Starting services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 5

# Check service health
echo ""
echo "🔍 Checking service health..."

# Check Streamlit app
if curl -s http://localhost:8501/_stcore/health > /dev/null 2>&1; then
    echo "  ✅ Streamlit App: Running"
else
    echo "  ⏳ Streamlit App: Starting..."
fi

# Check GPT-OSS server
if curl -s http://localhost:5001/health > /dev/null 2>&1; then
    echo "  ✅ GPT-OSS Server: Running"
else
    echo "  ⏳ GPT-OSS Server: Starting (may take 1-2 minutes)..."
fi

# Check Qwen server
if curl -s http://localhost:5002/health > /dev/null 2>&1; then
    echo "  ✅ Qwen Server: Running"
else
    echo "  ⏳ Qwen Server: Starting (may take 1-2 minutes)..."
fi

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📊 Access the application:"
echo "   Streamlit App:    http://localhost:8501"
echo "   GPT-OSS Server:   http://localhost:5001"
echo "   Qwen Server:      http://localhost:5002"
echo ""
echo "📝 Useful commands:"
echo "   View logs:        docker-compose logs -f"
echo "   Stop services:    docker-compose down"
echo "   Restart:          docker-compose restart"
echo "   Shell access:     docker exec -it ai-homework-grader bash"
echo ""
echo "⚠️  Note: Model servers may take 1-2 minutes to fully load"
echo ""
