.PHONY: dev backend frontend install clean

# Run both backend and frontend
dev:
	@echo "Starting backend and frontend..."
	@make -j2 backend frontend

# Backend only
backend:
	cd backend && uvicorn app.main:app --reload --port 8000

# Frontend only  
frontend:
	cd frontend && npm run dev

# Install all dependencies
install:
	cd backend && pip install -e ".[dev]"
	cd frontend && npm install

# Clean build artifacts
clean:
	rm -rf backend/__pycache__ backend/app/__pycache__
	rm -rf frontend/node_modules frontend/dist
