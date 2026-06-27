#!/bin/bash
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "Starting Backend..."
uvicorn backend.main:app --reload --port 8000 &
BACKEND_PID=$!

echo "Starting Frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!

echo "Running Ranking..."
cd "$PROJECT_ROOT"
python rank.py

echo "Validating Output..."
python "../[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/validate_submission.py" "../[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/submission.csv"

echo "Setup complete. Backend PID: $BACKEND_PID, Frontend PID: $FRONTEND_PID"
wait
