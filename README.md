\# Entity Databoard Application

A full-stack application for managing entity data with a FastAPI backend and React frontend.

## Project Structure

- `backend/` - FastAPI server that connects to Supabase database
- `frontend/` - React application with a two-section databoard UI

## Quick Start

For Windows users, a convenient startup script is provided:

```bash
start.bat
```

This will start both the backend and frontend servers in separate command prompts.

## Manual Setup

### Backend Setup

1. Create a virtual environment (already done):
```bash
python -m venv venv
```

2. On Windows, activate the virtual environment and install dependencies:
```bash
# On Windows
venv\Scripts\activate
pip install -r requirements.txt
```

3. Start the backend server:
```bash
python main.py
```

The API will be available at http://localhost:8000

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
npm start
```

The frontend will be available at http://localhost:3000

## Features

### Backend API

- `GET /entities` - Get all entities
- `GET /entity/{entity_id}` - Get an entity by ID
- `POST /entity` - Create a new entity
