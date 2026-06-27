@echo off
pushd %~dp0..
echo Starting Backend...
start "Backend" uvicorn backend.main:app --reload --port 8000
echo Starting Frontend...
cd frontend
start "Frontend" npm run dev
echo Running Ranking...
cd ..
python rank.py
echo Validating Output...
python "..\\[PUB\\] India_runs_data_and_ai_challenge\\India_runs_data_and_ai_challenge\\validate_submission.py" "..\\[PUB\\] India_runs_data_and_ai_challenge\\India_runs_data_and_ai_challenge\\submission.csv"
popd
pause
