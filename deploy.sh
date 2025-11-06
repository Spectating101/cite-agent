#!/bin/bash

# ============================================================================
# Cite-Agent Automated Deployment Script
# Usage: ./deploy.sh [environment]
# Example: ./deploy.sh production
# ============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker not found. Please install Docker first."
        exit 1
    fi
    log_success "Docker found: $(docker --version)"

    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose not found. Please install Docker Compose first."
        exit 1
    fi
    log_success "Docker Compose found: $(docker-compose --version)"

    # Check if running as root
    if [ "$EUID" -eq 0 ]; then
        log_warning "Running as root. Consider using a non-root user with docker group."
    fi
}

# Setup environment
setup_environment() {
    log_info "Setting up environment..."

    if [ ! -f .env ]; then
        log_info "Creating .env from template..."
        cp .env.example .env
        log_warning "Please edit .env and add your API keys before continuing!"
        read -p "Press Enter once you've configured .env, or Ctrl+C to exit..."
    else
        log_info ".env file already exists"
    fi

    # Validate required variables
    log_info "Validating environment configuration..."

    if ! grep -q "^GROQ_API_KEY=gsk_" .env 2>/dev/null && \
       ! grep -q "^CEREBRAS_API_KEY=.\\{20,\\}" .env 2>/dev/null; then
        log_error "No valid API key found in .env. Please add at least GROQ_API_KEY or CEREBRAS_API_KEY"
        exit 1
    fi

    if grep -q "^JWT_SECRET=change_me" .env 2>/dev/null; then
        log_warning "JWT_SECRET not changed from default. Generating secure secret..."
        NEW_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(64))" 2>/dev/null || openssl rand -base64 64)
        sed -i.bak "s/JWT_SECRET=change_me.*/JWT_SECRET=$NEW_SECRET/" .env
        log_success "Generated secure JWT_SECRET"
    fi

    log_success "Environment configuration validated"
}

# Create required directories
create_directories() {
    log_info "Creating required directories..."
    mkdir -p monitoring/grafana/dashboards monitoring/grafana/datasources
    mkdir -p logs
    log_success "Directories created"
}

# Pull latest images
pull_images() {
    log_info "Pulling latest Docker images..."
    docker-compose pull
    log_success "Images pulled"
}

# Build custom images
build_images() {
    log_info "Building custom images..."
    docker-compose build --no-cache
    log_success "Images built"
}

# Start services
start_services() {
    log_info "Starting services..."

    # Start with dependencies first
    log_info "Starting database and cache..."
    docker-compose up -d postgres redis

    # Wait for healthy database
    log_info "Waiting for database to be ready..."
    timeout=60
    counter=0
    until docker-compose exec -T postgres pg_isready -U cite_agent > /dev/null 2>&1; do
        counter=$((counter + 1))
        if [ $counter -gt $timeout ]; then
            log_error "Database failed to start within ${timeout}s"
            docker-compose logs postgres
            exit 1
        fi
        sleep 1
    done
    log_success "Database is ready"

    # Start remaining services
    log_info "Starting API and monitoring stack..."
    docker-compose up -d

    log_success "All services started"
}

# Wait for services to be healthy
wait_for_health() {
    log_info "Waiting for services to be healthy..."

    # Wait for API
    log_info "Checking API health..."
    timeout=90
    counter=0
    until curl -f http://localhost:8000/health > /dev/null 2>&1; do
        counter=$((counter + 1))
        if [ $counter -gt $timeout ]; then
            log_error "API failed to become healthy within ${timeout}s"
            docker-compose logs api
            exit 1
        fi
        sleep 1
    done
    log_success "API is healthy"

    # Wait for Grafana
    log_info "Checking Grafana..."
    timeout=60
    counter=0
    until curl -f http://localhost:3000/api/health > /dev/null 2>&1; do
        counter=$((counter + 1))
        if [ $counter -gt $timeout ]; then
            log_warning "Grafana not responding (this is optional)"
            break
        fi
        sleep 1
    done

    if curl -f http://localhost:3000/api/health > /dev/null 2>&1; then
        log_success "Grafana is healthy"
    fi
}

# Run smoke tests
run_smoke_tests() {
    log_info "Running smoke tests..."

    # Test health endpoint
    log_info "Testing /health endpoint..."
    if ! curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_error "Health check failed"
        exit 1
    fi
    log_success "Health check passed"

    # Test metrics endpoint
    log_info "Testing /metrics endpoint..."
    if ! curl -f http://localhost:8000/metrics > /dev/null 2>&1; then
        log_warning "Metrics endpoint not responding (may not be critical)"
    else
        log_success "Metrics endpoint accessible"
    fi

    log_success "Smoke tests passed"
}

# Print service info
print_service_info() {
    echo ""
    echo "======================================================================="
    echo "  🎉 Cite-Agent Deployment Successful!"
    echo "======================================================================="
    echo ""
    echo "Services running:"
    docker-compose ps
    echo ""
    echo "Access URLs:"
    echo "  📝 API:        http://localhost:8000"
    echo "  📊 Grafana:    http://localhost:3000 (admin/admin)"
    echo "  📈 Prometheus: http://localhost:9090"
    echo "  🔍 Metrics:    http://localhost:8000/metrics"
    echo ""
    echo "Quick commands:"
    echo "  View logs:     docker-compose logs -f"
    echo "  Stop services: docker-compose down"
    echo "  Restart API:   docker-compose restart api"
    echo ""
    echo "Next steps:"
    echo "  1. Access Grafana dashboard at http://localhost:3000"
    echo "  2. Test API with: curl http://localhost:8000/health"
    echo "  3. Check logs: docker-compose logs -f api"
    echo "  4. See full guide: cat DEPLOY.md"
    echo ""
    echo "======================================================================="
}

# Main deployment flow
main() {
    echo "======================================================================="
    echo "  Cite-Agent Automated Deployment"
    echo "======================================================================="
    echo ""

    check_prerequisites
    setup_environment
    create_directories
    pull_images

    # Ask if should build
    read -p "Build custom images? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        build_images
    fi

    start_services
    wait_for_health
    run_smoke_tests
    print_service_info

    log_success "Deployment complete!"
}

# Run main
main "$@"
