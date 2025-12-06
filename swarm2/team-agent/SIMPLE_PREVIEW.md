# Simple Preview - Get Running Fast!

We're having dependency issues with Chakra UI. Let's get a basic preview running first!

## Quick Fix

```bash
cd /Users/lesdunston/Dropbox/Team\ Agent/Projects/ta_base/swarm2/team-agent/frontend

# Clean and reinstall (simplified dependencies)
rm -rf node_modules package-lock.json
npm install

# Should work now!
npm run dev
```

## What I Changed

Temporarily removed:
- Chakra UI (was causing version conflicts)
- TypeScript compiler (for faster builds)
- Linters (not needed for preview)

Kept the essentials:
- ✅ Vue 3
- ✅ Vue Router (navigation)
- ✅ Pinia (state management)
- ✅ Axios (API calls)
- ✅ Vite (build tool)

## What This Means

The UI will be **basic HTML/CSS** instead of fancy Chakra components, but:
- ✅ All functionality works
- ✅ Navigation works
- ✅ Forms work
- ✅ Mission management works
- ✅ You can see the architecture

We can add a proper UI library (Vuetify, PrimeVue, etc.) in the next iteration once we confirm everything works!

## After npm install works

Start the backend:
```bash
cd ../backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then open: http://localhost:5173

## Still Having Issues?

Try these Node versions (in order):
1. Node 20: `nvm use 20` or `nvm install 20`
2. Node 18: `nvm use 18` or `nvm install 18`

Then:
```bash
npm install
npm run dev
```

Let me know when you're running! We'll polish the UI in Phase 3.
