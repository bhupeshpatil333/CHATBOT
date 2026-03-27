# Chatbot Application Setup and Start Guide

This document contains instructions to configure and run the entire Helpdesk Chatbot application locally. The project contains a backend API managed by Python (FastAPI) and a frontend UI framework managed by Angular.

---

## 🏗️ Requirements
Ensure you have the following installed on your machine (Windows):
- Python 3.8+
- Node.js & npm (v18 or higher recommended)
- Angular CLI (optional but usually needed globally: `npm install -g @angular/cli`)

---

## 🐍 1. Backend Setup (Python / FastAPI)

The backend code is located in the `HelpdeskPythonAPI` directory. It uses a local SQLite database (`helpdesk.db`).

### **Steps to Start the Backend:**

1. **Open a new terminal** and navigate to the backend directory:
   ```cmd
   cd HelpdeskPythonAPI
   ```

2. **Activate the Virtual Environment:**
   A virtual environment (`venv`) is already created. You must activate it before running Python commands or installing packages.
   - For **Command Prompt (cmd)**:
     ```cmd
     venv\Scripts\activate.bat
     ```
   - For **PowerShell**:
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - *(Note: If `venv` gets deleted, recreate it using: `python -m venv venv`)*

3. **Install Requirements:**
   Install backend dependencies including FastAPI and SQLAlchemy.
   ```cmd
   pip install -r requirements.txt
   ```

4. **Start the API Server:**
   The backend API is hosted using `uvicorn`. Start it in development mode (with hot-reloading).
   ```cmd
   uvicorn main:app --reload
   ```

   **Backend URLs:**
   - Base URL: `http://127.0.0.1:8000` (or `http://localhost:8000`)
   - Swagger API Documentation: `http://127.0.0.1:8000/docs`

> **Note on AI Fallback:** The Python API optionally connects to Google Dialogflow for an AI fallback. Ensure the environment variable `DIALOGFLOW_PROJECT_ID` is set if you want to use that feature, otherwise, it gracefully returns a default support message.

---

## 🅰️ 2. Frontend Setup (Angular)

The frontend code is located in the `helpdesk-ui` directory. It communicates with the Python API. The CORS configuration in the API explicitly allows requests coming from `http://localhost:4200`.

### **Steps to Start the Frontend:**

1. **Open a second terminal** (keep the backend terminal running).
2. **Navigate to the frontend directory:**
   ```cmd
   cd helpdesk-ui
   ```

3. **Install Node.js Dependencies:**
   Install all the packages listed in `package.json` (like Angular Material). This only needs to be run once unless you change dependencies.
   ```cmd
   npm install
   ```

4. **Start the Angular Development Server:**
   ```cmd
   npm start
   ```
   *(Or run `ng serve` directly if Angular CLI is globally installed).*

   **Frontend URL:**
   - The application will be running at `http://localhost:4200/`

---

## 🚀 Short Run Commands

To start the applications directly in PowerShell, use these short commands:

**Terminal 1 (Backend):**
```powershell
cd c:\Users\bhupesh\Desktop\Angular_Developer\Task_Projects\CHATBOT\HelpdeskPythonAPI
.\venv\Scripts\uvicorn.exe main:app --reload
```

**Terminal 2 (Frontend):**
```cmd
cd c:\Users\bhupesh\Desktop\Angular_Developer\Task_Projects\CHATBOT\helpdesk-ui
npm start
```
