# RankForge – Intelligent Candidate Ranking Engine

### Candidate Discovery and Ranking System for INDIA RUNS 2026

RankForge is an intelligent candidate ranking system designed to evaluate resumes using semantic understanding and multi-factor scoring instead of traditional keyword filtering.

The system transforms raw candidate data into ranked, explainable recommendations through a hybrid retrieval and ranking pipeline.

---

## 🚀 Key Features

* **Hybrid Ranking Pipeline**
  Combines TF-IDF retrieval with semantic reranking using Sentence Transformers.

* **Explainable Ranking**
  Generates transparent score contributions and ranking explanations for each candidate.

* **Multi-Factor Evaluation**
  Uses multiple candidate signals beyond keyword matching.

* **Profile Quality Detection**
  Identifies suspicious, low-quality, or inflated candidate profiles.

* **Offline Execution Support**
  Runs without cloud APIs and supports local inference.

* **Interactive Dashboard**
  Includes leaderboard, metrics, candidate explorer, and explainability views.

---

## 🛠 System Architecture

### 1. Data Processing

* Candidate ingestion
* Data normalization
* Feature preparation

Modules:

* `loader.py`
* `flatten.py`

---

### 2. Ranking Engine

* Retrieval scoring
* Semantic similarity
* Feature extraction

Modules:

* `retrieval.py`
* `features.py`
* `scoring.py`

---

### 3. Service Layer

* FastAPI backend
* React frontend dashboard

Folders:

* `backend/`
* `frontend/`

---

## 📊 Multi-Factor Ranking Model

Final score is computed using weighted signals.

| Factor             | Weight |
| ------------------ | ------ |
| Semantic Score     | 25%    |
| Retrieval Score    | 25%    |
| Production Score   | 20%    |
| Career Score       | 10%    |
| Behavior Score     | 10%    |
| Availability Score | 5%     |
| Trust Score        | 5%     |

---

## 🧠 Candidate Evaluation Logic

The system evaluates:

* Semantic relevance to Job Description
* Technical skill alignment
* Production experience evidence
* Career progression
* Behavioral indicators
* Availability signals
* Profile reliability

Unlike traditional ATS systems, ranking is not based only on keyword matching.

---

## 🏃 How to Run

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Execute Ranking

```bash
python rank.py
```

### Start Backend

```bash
uvicorn backend.main:app --reload
```

### Start Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## 📡 API Endpoints

| Endpoint          | Purpose                |
| ----------------- | ---------------------- |
| `/top100`         | View ranked candidates |
| `/candidate/{id}` | Candidate details      |
| `/metrics`        | Dashboard metrics      |
| `/run`            | Execute ranking        |
| `/validate`       | Validate submission    |
| `/download`       | Download submission    |

---

## 📈 Performance

Target Runtime: **< 5 minutes**

Approximate execution:

* Loading → ~15 sec
* Feature Processing → ~45 sec
* Retrieval → ~60 sec
* Semantic Ranking → ~90 sec
* Total → ~3–5 min (CPU)

---

## 📂 Repository Structure

```text
redrob-ai-recruiter/
│
├── backend/
├── frontend/
├── models/
├── outputs/
├── scripts/
├── src/
├── tests/
├── utils/
├── rank.py
├── config.py
├── requirements.txt
└── README.md
```

---

## 🛡 Validation

Validate generated submission:

```bash
python validate_submission.py submission.csv
```

---

## 📦 Submission Assets

* GitHub Repository
* Demo Video
* submission.csv
* Documentation
* Validation Report

---

## 🏆 Project Goal

Build an intelligent candidate ranking system that replaces traditional keyword-based filtering with explainable and scalable ranking methods.

Designed for the INDIA RUNS 2026 challenge.

## 🎥 Demo Video

Watch the project demo here:
https://youtu.be/9btYR6TO9sw