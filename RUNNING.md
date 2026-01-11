# Running Genesis Locally (Windows)

These steps start the Collective Consciousness app on port 5003 using PowerShell.

## Prerequisites
- Python 3.11+ available on your PATH
- Git (only needed if you are cloning)

## Setup (first time)
Run these from the repo root `c:\Users\chaos\Genesis-1`:
1) Create a virtual environment  
`python -m venv .venv`
2) Activate it  
```
.\.venv\Scripts\activate
```
3) Install the minimal dependencies used by the app  
`pip install flask flask-cors`

## Start the app
From the repo root:
```
Start-Process -FilePath ".\.venv\Scripts\python.exe" `
  -ArgumentList "collective_consciousness_home.py" `
  -WorkingDirectory ".\Genesis" `
  -RedirectStandardOutput ".\collective_server.out" `
  -RedirectStandardError ".\collective_server.err"
```
This launches the Flask dev server on `http://127.0.0.1:5003` with logs in `collective_server.out` and `collective_server.err`.

## Stop the app
- If you started it in the foreground, press Ctrl+C in that window.
- If you used `Start-Process`, stop it with:  
`Get-Process -Path "$PWD\.venv\Scripts\python.exe" | Stop-Process`

## Verify
Check that it is responding:  
`Invoke-WebRequest -UseBasicParsing http://127.0.0.1:5003/ | Select-Object -ExpandProperty StatusCode`

## Data locations
- Conversation DB: `C:\home\ubuntu\collective_memory.db`
- App data JSON files: `C:\home\ubuntu\synthsara_data\` (created automatically)

## Notes
- The app auto-generates `Genesis/templates/collective_home.html` at startup.
- Running via `collective_consciousness_home.py` uses Flask debug mode with auto-reload; for production, wrap it with a real WSGI server.
