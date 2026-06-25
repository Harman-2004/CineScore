# CineScore 🎬

CineScore is a next-generation, AI-powered movie review and rating platform that calculates smarter, more honest cinematic scores. Instead of relying solely on conventional aggregate ratings, CineScore applies Natural Language Processing (NLP) and machine learning to analyze reviewer sentiment, moderate spam, scrape real-time social feedback, and generate vector-based personalized recommendations.

---

## 🚀 Key Features

*   **Composite AI Scoring (CineScore)**: Combines ratings from TMDb, IMDb, Metacritic, and YouTube comments with custom sentiment polarity weights to yield a highly balanced aggregate score.
*   **Aspect-Based Sentiment Analysis**: Leverages NLP to evaluate review transcripts across critical cinematic dimensions: *Acting*, *Story*, *Music*, *Visual Effects*, and *Direction*.
*   **Review Integrity & Bot Moderation**: Employs heuristics to detect copy-paste spam, repetitive reviewer patterns, and bot activity, ensuring trustworthy reviews.
*   **Hybrid Recommendation Engine**: Computes high-fidelity recommendations using content embeddings (`SentenceTransformers`) combined with user preference matrices.
*   **Real-time YouTube Scraper**: Automatically pulls and processes public comments from movie trailers to incorporate fresh viewer opinions immediately.
*   **Stunning UI/UX Dashboard**: Designed with a premium dark-themed glassmorphism aesthetic, offering rich interactive charts, aspect breakdowns, and review breakdowns.

---

## 🛠️ Technology Stack

### Backend (API & ML Pipeline)
*   **FastAPI**: High-performance, asynchronous web framework.
*   **PostgreSQL (Neon DB)**: Managed cloud database for scalable persistence.
*   **SQLAlchemy / Alembic**: ORM and migration handling.
*   **SentenceTransformers**: Vector embedding generation for AI-powered recommendation matching.
*   **TextBlob**: NLP sentiment analysis.

### Frontend
*   **React (Vite)**: Fast, modern client-side environment.
*   **Recharts**: Premium data visualization for sentiment metrics, integrity logs, and rating comparisons.
*   **Vanilla CSS**: Sleek custom design with responsive glassmorphic cards and smooth micro-animations.

---

## 📂 Project Structure

```
cine-score/
├── backend/                  # FastAPI Application
│   ├── app/
│   │   ├── models/           # SQLAlchemy DB Models
│   │   ├── routers/          # API Endpoints (standard REST, movies, reviews, recommendations)
│   │   ├── schemas/          # Pydantic schemas/DTOs
│   │   ├── services/         # Scrapers, scoring algorithm, recommendation engine
│   │   └── sentiment/        # NLP analyzer
│   └── tests/                # Pytest suites
└── frontend/                 # React Frontend
    ├── src/                  # React components, style sheets, and page logic
    └── public/               # Static assets
```

---

## ⚙️ Local Development Setup

### 1. Prerequisites
Ensure you have the following installed on your machine:
*   Python 3.10+
*   Node.js 18+

### 2. Backend Setup
1.  Navigate to the `backend` directory:
    ```bash
    cd backend
    ```
2.  Create and activate a virtual environment:
    ```bash
    python -m venv venv
    # On Windows:
    venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Create a `.env` file in the `backend/` root directory (see `.env.example`):
    ```env
    # Security Config
    SECRET_KEY=your_secret_key_here
    ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=60

    # Database Connection
    DATABASE_URL=postgresql://user:pass@host/dbname?sslmode=require

    # Third-Party Integrations
    TMDB_API_KEY=your_tmdb_api_key
    OMDB_API_KEY=your_omdb_api_key
    YOUTUBE_API_KEY=your_youtube_api_key

    # CORS configuration
    BACKEND_CORS_ORIGINS=http://localhost:5173,http://localhost:3000
    ENVIRONMENT=development
    ```
5.  Start the development server:
    ```bash
    uvicorn app.main:app --reload
    ```
    The API docs will be available at `http://localhost:8000/docs`.

### 3. Frontend Setup
1.  Navigate to the `frontend` directory:
    ```bash
    cd ../frontend
    ```
2.  Install packages:
    ```bash
    npm install
    ```
3.  Create a `.env` file in the `frontend/` directory:
    ```env
    VITE_API_URL=http://localhost:8000
    ```
4.  Launch the client:
    ```bash
    npm run dev
    ```
    Open `http://localhost:5173` in your browser.

---

## 🧪 Running Tests
To run backend unit and integration tests:
```bash
cd backend
python -m pytest
```

---

## 🚀 Deployment

*   **Backend**: Deployed on **Railway** (linked to GitHub for CD). Ensure environment variables match your backend `.env` keys.
*   **Frontend**: Deployed on **Vercel** with the configuration pointing to the production Railway endpoint URL as `VITE_API_URL`.
