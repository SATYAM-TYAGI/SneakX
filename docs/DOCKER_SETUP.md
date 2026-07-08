# Docker Setup

I split this application into two Docker containers: one for the React frontend and one for the FastAPI backend. This means you can run the app without installing Python, Node.js, or any machine learning libraries on your computer.

---

## Containers and Ports

I set up the network so the two containers can talk to each other:

* **Backend Container**: Runs on port `8000`. It handles all the recommendation math and API endpoints.
* **Frontend Container**: Runs on port `3000`. It serves the React website.

---

## The Configuration Files

### 1. Root Orchestrator (`docker-compose.yml`)
I put this file in the root folder. It starts both containers at the same time. It also configures a shared network so the frontend React app can send requests to the FastAPI backend.

### 2. Backend (`backend/Dockerfile`)
I chose a lightweight Python 3.10 image. 
* It installs the dependencies like FastAPI, Pandas, and Sentence Transformers.
* It copies all the backend files, including the pre-saved data and embeddings in the `data/` folder.
* It starts the FastAPI server using Uvicorn.

### 3. Frontend (`frontend/Dockerfile`)
I used a Node.js image to compile and run the React app.
* It copies the package files and runs `npm install`.
* It copies the React code and assets.
* It starts the Vite development server.

---

## Running the App

Just open your terminal in the root folder and run:
```bash
docker compose up
```

If you want to stop it, press `Ctrl + C` or run:
```bash
docker compose down
```
If you want to run it in the background, you can use:
```bash
docker compose up -d
```
