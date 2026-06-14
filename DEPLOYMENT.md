# CineScore Production Deployment Guide

This document outlines the steps required to migrate CineScore from a local SQLite database to a serverless **Neon PostgreSQL** database and deploy the platform to cloud hosting providers like **Railway** or **Render**.

---

## 1. Neon PostgreSQL Database Setup

[Neon](https://neon.tech/) provides serverless, highly-scalable PostgreSQL databases.

1. **Sign Up:** Go to [Neon.tech](https://neon.tech/) and create a free account.
2. **Create Project:** Create a new project (e.g., `cinescore-db`). Select your preferred region and click **Create Project**.
3. **Copy Connection String:** Once created, you will be redirected to the dashboard. Copy the provided connection string from the **Connection Details** section. It will look like this:
   ```env
   postgresql://alex:AbCdEf1234@ep-cool-name.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```
4. **Save String:** Save this connection string; it will be configured as the `DATABASE_URL` environment variable.

---

## 2. Environment Variables Configuration

Create a `.env` file in your root workspace or backend root using the template in [backend/.env.example](file:///c:/Users/ACER/Downloads/movie-ai-rating%20(2)%20(1)/movie-ai-rating/movie-ai-rating/backend/.env.example):

| Variable | Description | Requirement |
| :--- | :--- | :--- |
| `DATABASE_URL` | PostgreSQL connection URL (e.g., from Neon). | **Required** in Production |
| `SECRET_KEY` | JWT secret signing token (e.g., a long random string). | **Required** (must be unique in Production) |
| `ENVIRONMENT` | Defines app mode (`development` or `production`). | Optional (defaults to `development`) |
| `TMDB_API_KEY` | Key for TMDb API metadata extraction. | Optional (falls back to mock metadata) |
| `OMDB_API_KEY` | Key for OMDb official scores. | Optional (falls back to mock scores) |
| `YOUTUBE_API_KEY` | Key for YouTube scraper & review analysis. | Optional (falls back to mock transcripts) |

---

## 3. Local Testing with PostgreSQL

To verify that the application operates correctly with your Neon PostgreSQL instance:

1. **Set Local Environment:** Update your local `.env` file in the project:
   ```env
   ENVIRONMENT=development
   DATABASE_URL=postgresql://<user>:<password>@<host>/<database>?sslmode=require
   SECRET_KEY=yoursecretkeyhere
   ```
2. **Run Startup Migrations:** Start the backend. CineScore will automatically connect, verify the database schema, perform database-agnostic column migrations, and seed the default user:
   ```powershell
   cd backend
   python -m uvicorn app.main:app --reload
   ```
3. **Execute Backend Tests:** Run pytest to verify all tables, auth, reviews, and scoring work seamlessly on the new configuration:
   ```powershell
   python -m pytest
   ```

---

## 4. Production Deployment

### Option A: Railway (Git-Driven Auto-Deployment)

[Railway](https://railway.com/) connects directly to your GitHub repository and automatically deploys modifications whenever you push.

1. **Push Changes:** Ensure your CineScore codebase modifications are pushed to your GitHub repository:
   ```powershell
   git add .
   git commit -m "Configure production database migration and startup validation"
   git push origin main
   ```
2. **Add Service:** Go to [Railway](https://railway.com/), create a new project, select **Deploy from GitHub repo**, and select your `CineScore` repository.
3. **Configure Build Settings:**
   * **Root Directory:** Set root to `/` or select the `backend` folder.
   * **Build Command:** `pip install -r requirements.txt` (handled automatically by Nixpacks).
   * **Start Command:** `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. **Set Environment Variables:** In the Railway dashboard under **Variables**, click **New Variable** and add the keys from your `.env`:
   * `DATABASE_URL` (your Neon connection string)
   * `SECRET_KEY` (secure generated token)
   * `ENVIRONMENT` = `production`
   * `TMDB_API_KEY`, `OMDB_API_KEY`, `YOUTUBE_API_KEY` (optional)
5. **Deploy:** Click **Deploy**. Railway will build the Docker container/Nixpack service and provision a public URL.

### Option B: Render Deployment

1. **Web Service Setup:** Log in to [Render](https://render.com/), create a **New Web Service**, and link your GitHub repository.
2. **Configure Settings:**
   * **Environment:** `Python`
   * **Root Directory:** `backend`
   * **Build Command:** `pip install -r requirements.txt`
   * **Start Command:** `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. **Configure Environment Variables:** Under **Advanced**, click **Add Environment Variable** and enter:
   * `DATABASE_URL` = (Neon PostgreSQL URL)
   * `SECRET_KEY` = (Secure JWT key)
   * `ENVIRONMENT` = `production`
   * `TMDB_API_KEY`, `OMDB_API_KEY`, `YOUTUBE_API_KEY` (as needed)
4. **Deploy:** Click **Create Web Service**. Render will build the environment and start the Uvicorn server.
