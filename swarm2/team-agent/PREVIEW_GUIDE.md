# Team Agent Frontend Preview Guide

## 🎉 Phase 2 Complete - Mission Management UI

This guide will help you preview the Team Agent frontend with complete Mission Management functionality.

## What's Implemented

### ✅ Mission Management (Phase 2 - Complete)
- **Mission Create Form** - Create missions with capability requirements, breakpoints, and auto-approval settings
- **Mission List View** - Browse all missions with filtering (All/Active/Completed/Failed)
- **Mission Detail View** - Track workflow progress with visual timeline
- **Workflow Timeline** - See each stage's status, timestamps, and output
- **Breakpoint Approval** - Review and approve capability selections
- **Real-time Updates** - WebSocket integration for live progress tracking

### 🎨 UI Components
- Responsive Chakra UI design
- Loading states and error handling
- Empty states with helpful guidance
- Form validation
- Status badges and progress indicators

## Quick Start Options

### Option 1: Docker Compose (Recommended)

```bash
cd /Users/lesdunston/Dropbox/Team\ Agent/Projects/ta_base/swarm2/team-agent

# Start frontend + backend + ELK stack
docker-compose -f docker-compose.dev.yml up
```

**Access:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:5000
- Kibana Logs: http://localhost:5601

### Option 2: Manual Setup

**Terminal 1 - Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Terminal 2 - Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

**Access:**
- Frontend: http://localhost:5173
- Backend: http://localhost:5000

## Preview Tour

### 1. Dashboard (/)
- Overview of system stats
- Quick navigation to all features

### 2. Create Mission (/missions/create)
**Try this:**
1. Enter a description: "Build a REST API for user management"
2. Add capabilities:
   - Type: Code Generation
   - Min Trust Score: 75
3. Select breakpoints:
   - ✅ Capability Selection
   - ✅ Design Approval
4. Click "Submit Mission"

### 3. Mission List (/missions)
**Features:**
- Tab filtering (All/Active/Completed/Failed)
- Mission cards with progress indicators
- Click any mission to view details

### 4. Mission Detail (/missions/:id)
**Explore:**
- Progress overview with percentage
- Workflow stage timeline showing:
  - Stage status (pending/running/completed/failed)
  - Timestamps and duration
  - Stage outputs
- Mission details sidebar
- Auto-refresh every 5 seconds for active workflows
- Actions menu (Refresh/Resume/Cancel)

### 5. Breakpoint Approval (Modal)
**When a mission hits a breakpoint:**
1. "Approval Required" banner appears
2. Click "Review & Approve"
3. See capability options with:
   - Match scores
   - Trust scores
   - Pricing
4. Select an option and approve

## Mock Data

Since the backend services return mock data currently, you'll see:
- Empty mission lists initially
- Missions you create will appear with pending status
- Real integration with OrchestratorA2A comes in the next phase

## Testing Checklist

### Mission Creation
- [ ] Form validates required fields
- [ ] Can add/remove capabilities
- [ ] Capability type dropdown works
- [ ] Min trust score slider updates
- [ ] Breakpoint checkboxes toggle
- [ ] Auto-approval settings work
- [ ] Submit creates mission and navigates to detail

### Mission List
- [ ] Loading spinner appears
- [ ] Empty state shows when no missions
- [ ] Tab filtering updates counts
- [ ] Mission cards display correctly
- [ ] Click card navigates to detail
- [ ] Responsive grid layout works

### Mission Detail
- [ ] Back button returns to list
- [ ] Progress bar displays correctly
- [ ] Timeline shows stage status
- [ ] Timestamps format properly
- [ ] Actions menu opens
- [ ] Refresh button works
- [ ] Breakpoint modal opens when needed

### Breakpoint Modal
- [ ] Options display with all details
- [ ] Radio selection works
- [ ] Match/trust scores visible
- [ ] Approve button enables when option selected
- [ ] Reject button works
- [ ] Close button dismisses modal

## Component Architecture

```
MissionCreateView
  └─ MissionCreateForm (with validation)

MissionListView
  └─ MissionCard (displays mission summary)

MissionDetailView
  ├─ WorkflowStageTimeline (visual progress)
  ├─ BreakpointApprovalModal (capability selection)
  └─ useWorkflowWebSocket (real-time updates)
```

## API Endpoints Used

```
POST   /api/mission/submit
GET    /api/mission/list
GET    /api/mission/workflow/:id/status
POST   /api/mission/breakpoint/:id/approve
POST   /api/mission/breakpoint/:id/reject
WS     /ws/workflow/:id
```

## Known Limitations (To Be Implemented)

1. **Backend Integration**: Services return mock data
   - Next: Connect to OrchestratorA2A
   - Next: Integrate with WorkflowTape

2. **WebSocket Events**: WebSocket connects but needs backend handlers
   - Next: Implement Flask-SocketIO event broadcasting

3. **Error Handling**: Console logs instead of toast notifications
   - Next: Add toast notification system

4. **Authentication**: No auth yet
   - Next: Add JWT token handling

## Troubleshooting

### Frontend won't start
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### TypeScript errors
```bash
cd frontend
npm run build  # Check for compilation errors
```

### Backend won't start
```bash
cd backend
pip install -r requirements.txt --upgrade
python app.py
```

### Port conflicts
If ports 5173 or 5000 are in use:
```bash
# Frontend: Edit frontend/vite.config.ts
server: { port: 5174 }

# Backend: Edit backend/app.py
socketio.run(app, port=5001)
```

## Next Steps (Phase 3)

After previewing Phase 2, we'll implement:
- **Trust Scoring Dashboard**: Agent reputation leaderboard with trust history graphs
- **Real-time trust score updates** via WebSocket
- **Agent detail pages** with metrics and event timelines

## Screenshots

**Mission Create Form:**
- Clean form layout with Chakra UI components
- Capability builder with add/remove
- Breakpoint checkboxes
- Submit/Cancel buttons

**Mission List:**
- Responsive grid of mission cards
- Tab filtering (All/Active/Completed/Failed)
- Progress indicators on cards
- Empty state guidance

**Mission Detail:**
- Progress overview with percentage
- Visual stage timeline
- Mission details sidebar
- Breakpoint approval banner

**Breakpoint Modal:**
- Capability options with scores
- Radio selection
- Approve/Reject actions

## Need Help?

Check the main documentation:
- `frontend/README.md` - Frontend architecture
- `backend/README.md` - Backend API docs
- `FRONTEND_BACKEND_README.md` - Complete overview

Enjoy exploring the Mission Management UI! 🚀
