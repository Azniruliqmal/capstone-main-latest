# How to Start the Development Servers

## Backend Server

### Option 1: Using the Python script
```bash
cd "C:\Users\User\Desktop\COHORT 3 PROJECT - GAMUDA AI\PROJECT\capstone-main-main\backend"
"C:/Users/User/Desktop/COHORT 3 PROJECT - GAMUDA AI/PROJECT/capstone-main-main/.venv/Scripts/python.exe" start_server.py
```

### Option 2: Using uvicorn directly
```bash
cd "C:\Users\User\Desktop\COHORT 3 PROJECT - GAMUDA AI\PROJECT\capstone-main-main\backend"
"C:/Users/User/Desktop/COHORT 3 PROJECT - GAMUDA AI/PROJECT/capstone-main-main/.venv/Scripts/uvicorn.exe" api.api:app --reload --host 0.0.0.0 --port 8000
```

### Option 3: Using the batch file
Double-click the `start_server.bat` file in the backend directory.

## Frontend Server

```bash
cd "C:\Users\User\Desktop\COHORT 3 PROJECT - GAMUDA AI\PROJECT\capstone-main-main\frontend"
npm run dev
```

## Testing the Fixes

Once both servers are running:

1. **Backend**: http://localhost:8000
2. **Frontend**: http://localhost:5173 (or the port shown in terminal)

### Test the Status Update Fix:
1. Navigate to Projects page
2. Click the 3-dot menu on any project card
3. Hover over "Change Status" 
4. Select a different status
5. Verify the status badge updates immediately
6. Check that status tab filtering works correctly

### Test the Card Layout Fix:
1. View the Projects page
2. Verify all cards have consistent height
3. Check that Budget, Scripts, Created info aligns at bottom
4. Confirm View Details button and 3-dot menu are on same level

## Troubleshooting

### If uvicorn is not found:
```bash
"C:/Users/User/Desktop/COHORT 3 PROJECT - GAMUDA AI/PROJECT/capstone-main-main/.venv/Scripts/python.exe" -m pip install uvicorn[standard]
```

### If FastAPI is not found:
```bash
"C:/Users/User/Desktop/COHORT 3 PROJECT - GAMUDA AI/PROJECT/capstone-main-main/.venv/Scripts/python.exe" -m pip install fastapi
```

### Database Issues:
The database will be automatically initialized when the server starts. If you see database errors, check the `init_db.py` file in the backend directory.

## Expected Output

### Backend Server:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Database tables created successfully
INFO:     Application startup complete.
```

### Frontend Server:
```
  VITE v4.x.x  ready in Xms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

## API Endpoints

With the backend running, you can test:
- http://localhost:8000/docs - FastAPI documentation
- http://localhost:8000/projects - Projects API
- http://localhost:8000/chat - Chat API (for AI Assistant)
