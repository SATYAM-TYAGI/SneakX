# Installation Guide

I made the setup process very easy. You do not need to install Python, Node.js, or any machine learning tools on your computer. Everything is packaged inside Docker.

## Prerequisiites
Make sure you have **Docker Desktop** installed and running on your computer.

---

## Setup Steps

### 1. Clone the repository
First, open your terminal and clone this repository:
```bash
git clone https://github.com/username/SneakX.git
cd SneakX
```

### 2. Run the application
Start the containers using Docker Compose:
```bash
docker compose up
```
Docker will download the images, build the frontend and backend, and start the services. 

### 3. Open the website
Once the terminal logs show that Vite is ready, open your web browser and go to:
`http://localhost:3000`

That is all! The app is fully plug-and-play and ready to use.
