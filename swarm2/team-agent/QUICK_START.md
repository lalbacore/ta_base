# Quick Start - Manual Setup (Recommended)

Docker is having issues, so let's run the frontend and backend manually!

## Prerequisites

- Node.js 18+ ([download here](https://nodejs.org/))
- Python 3.9+ (you already have this)

## Step 1: Start Frontend

```bash
cd /Users/lesdunston/Dropbox/Team\ Agent/Projects/ta_base/swarm2/team-agent/frontend

# Install dependencies (one time)
npm install

# Start dev server
npm run dev
```

**Expected output:**
```
VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

Keep this terminal open!

## Step 2: Start Backend (New Terminal)

```bash
cd /Users/lesdunston/Dropbox/Team\ Agent/Projects/ta_base/swarm2/team-agent/backend

# Create virtual environment (one time)
python -m venv venv

# Activate it
source venv/bin/activate  # On macOS/Linux
# OR on Windows:
# venv\Scripts\activate

# Install dependencies (one time)
pip install -r requirements.txt

# Start Flask server
python app.py
```

**Expected output:**
```
 * Running on http://127.0.0.1:5000
 * Running on http://127.0.0.1:5000
```

Keep this terminal open too!

## Step 3: Open Browser

Go to: **http://localhost:5173**

You should see the Team Agent dashboard!

## Quick Tour

### 1. Dashboard
- Click around the navigation
- See all the features listed

### 2. Create a Mission
- Click "Missions" in sidebar
- Click "+ Create Mission" button
- Fill out the form:
  - Description: "Build a REST API"
  - Click "Add Capability"
  - Select "Code Generation"
  - Check "Capability Selection" breakpoint
  - Click "Submit Mission"

### 3. View Missions
- You'll be taken to the mission detail page
- See the progress timeline
- Check the mission details sidebar

### 4. Mission List
- Click "Missions" in sidebar to see all missions
- Try the filter tabs (All/Active/Completed/Failed)

## Troubleshooting

### Frontend won't start

**Error: `Cannot find module`**
```bash
cd frontend
rm -rf node_modules
npm install
npm run dev
```

**Error: `Port 5173 is already in use`**
```bash
# Kill the process using port 5173
lsof -ti:5173 | xargs kill -9
# Then try again
npm run dev
```

### Backend won't start

**Error: `No module named 'flask'`**
```bash
# Make sure venv is activated (you should see (venv) in your prompt)
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

**Error: `Port 5000 is already in use`**
```bash
# Kill the process using port 5000
lsof -ti:5000 | xargs kill -9
# Then try again
python app.py
```

### Can't access http://localhost:5173

1. Check both terminals are running (no errors)
2. Try http://127.0.0.1:5173 instead
3. Check firewall settings

## What Works Right Now

✅ **Navigation** - All sidebar links work
✅ **Mission Creation** - Full form with validation
✅ **Mission List** - Grid view with filtering
✅ **Mission Details** - Timeline and progress
✅ **Responsive Design** - Works on different screen sizes

⏳ **Coming Soon** - Backend integration with real workflows

## Need Help?

The app is using **mock data** from the frontend stores right now. When you create a mission, it gets stored in the browser's memory (Pinia store) but won't persist when you refresh.

To see it working:
1. Create a mission
2. View it in the list
3. Click to see details
4. Don't refresh the page (data will be lost)

This is expected! Real backend integration is the next step.

---

**Enjoy exploring! 🚀**

Any questions, just ask!
