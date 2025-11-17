#!/bin/bash

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

IMAGE_NAME="stock-api"
CONTAINER_NAME="stock-api-container"
PORT=8000

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Stock Statistics API - Docker Setup  ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker is installed!${NC}"
docker --version
echo ""

if ! docker ps &> /dev/null; then
    echo -e "${RED}❌ Docker daemon is not running!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker daemon is running!${NC}"
echo ""

if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo -e "${YELLOW}⚠️  Existing container found. Removing...${NC}"
    docker rm -f ${CONTAINER_NAME} || true
    echo -e "${GREEN}✅ Old container removed!${NC}"
    echo ""
fi

if [ "$1" == "--rebuild" ]; then
    echo -e "${YELLOW}🔄 Rebuilding image from scratch...${NC}"
    docker rmi ${IMAGE_NAME}:latest || true
    echo ""
fi

echo -e "${BLUE}🔨 Building Docker image...${NC}"
echo ""

if docker build -t ${IMAGE_NAME}:latest .; then
    echo ""
    echo -e "${GREEN}✅ Image built successfully!${NC}"
    echo ""
else
    echo ""
    echo -e "${RED}❌ Build failed!${NC}"
    exit 1
fi

echo -e "${BLUE}🚀 Starting container...${NC}"
echo ""

if docker run -d \
    -p ${PORT}:${PORT} \
    --name ${CONTAINER_NAME} \
    ${IMAGE_NAME}:latest; then
    
    echo ""
    echo -e "${GREEN}✅ Container started successfully!${NC}"
    echo ""
else
    echo ""
    echo -e "${RED}❌ Failed to start container!${NC}"
    exit 1
fi

echo -e "${YELLOW}⏳ Waiting for API to be ready...${NC}"
sleep 3

if curl -s http://localhost:${PORT}/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ API is healthy and ready!${NC}"
else
    echo -e "${YELLOW}⚠️  API might still be starting...${NC}"
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║           🎉 ALL DONE! 🎉              ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📍 Access your API at:${NC}"
echo "   Frontend:    http://localhost:${PORT}"
echo "   API Docs:    http://localhost:${PORT}/docs"
echo "   Health:      http://localhost:${PORT}/health"
echo ""
echo -e "${BLUE}🛠️  Useful commands:${NC}"
echo "   View logs:   docker logs -f ${CONTAINER_NAME}"
echo "   Stop:        docker stop ${CONTAINER_NAME}"
echo "   Start:       docker start ${CONTAINER_NAME}"
echo "   Remove:      docker rm -f ${CONTAINER_NAME}"
echo "   Rebuild:     ./docker-setup.sh --rebuild"
echo ""
