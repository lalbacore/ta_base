# Team Agent Frontend

Vue 3 + TypeScript + Chakra UI frontend for the Team Agent multi-agent orchestration platform.

## Features

- **Dashboard**: Overview of active missions, trust scores, and certificate status
- **Mission Management**: Create and track workflow missions with breakpoint approvals
- **Trust Scoring**: Agent reputation tracking and trust metrics visualization
- **PKI Management**: Certificate lifecycle management with expiration monitoring
- **Capability Registry**: Browse and discover A2A capabilities
- **Governance**: Configure policies and view decision history
- **Artifacts**: View workflow manifests and verify cryptographic signatures
- **Logs**: Integrated Kibana dashboard for system logs

## Tech Stack

- **Framework**: Vue 3 with Composition API
- **Language**: TypeScript (strict mode)
- **Build Tool**: Vite
- **UI Library**: Chakra UI for Vue
- **State Management**: Pinia
- **Routing**: Vue Router
- **HTTP Client**: Axios
- **Charts**: Chart.js with vue-chartjs

## Project Structure

```
src/
├── main.ts                 # App entry point
├── App.vue                 # Root component
├── router/                 # Vue Router configuration
├── stores/                 # Pinia stores (mission, trust, pki, etc.)
├── services/               # API service layer
├── components/             # Reusable Vue components
│   ├── dashboard/
│   ├── mission/
│   ├── trust/
│   ├── pki/
│   ├── registry/
│   ├── governance/
│   ├── artifacts/
│   └── logs/
├── views/                  # Page components
├── types/                  # TypeScript type definitions
└── utils/                  # Utility functions
```

## Development

### Prerequisites

- Node.js 18+ and npm/yarn
- Python 3.9+ (for backend)

### Installation

```bash
npm install
```

### Run Development Server

```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### Build for Production

```bash
npm run build
```

### Run Tests

```bash
npm run test
```

### Lint

```bash
npm run lint
```

## Environment Variables

Create `.env.development` and `.env.production` files:

```env
VITE_API_BASE_URL=http://localhost:5000/api
VITE_WS_BASE_URL=ws://localhost:5000/ws
```

## API Integration

The frontend connects to the Flask backend API at the configured `VITE_API_BASE_URL`.

WebSocket connections are established via `VITE_WS_BASE_URL` for real-time updates:
- `/ws/workflow/{workflow_id}` - Mission progress updates
- `/ws/trust/updates` - Trust score changes
- `/ws/pki/events` - Certificate events

## Architecture

### State Management

Pinia stores manage application state with reactive getters and async actions:

- **Mission Store**: Workflow submissions, status tracking, breakpoint approvals
- **Trust Store**: Agent metrics, trust history, event logs
- **PKI Store**: Certificates, CRL data, audit logs
- **Registry Store**: Capabilities, providers, matching results
- **Governance Store**: Policy configuration, decisions, approval gates
- **WebSocket Store**: Real-time connection management

### Service Layer

Service classes wrap backend API calls with typed requests/responses:

- `MissionService`: Mission and workflow operations
- `TrustService`: Trust scoring and agent metrics
- `PKIService`: Certificate lifecycle management
- `RegistryService`: Capability discovery and matching
- `GovernanceService`: Policy management and approvals
- `ArtifactsService`: Manifest and signature verification

### Type Safety

All backend data models have matching TypeScript interfaces in `src/types/`.

TypeScript strict mode is enabled with no `any` types allowed.

## Phase 1 Status

✅ Vue 3 + Vite + TypeScript project setup
✅ Chakra UI configuration
✅ AppLayout with navigation
✅ Pinia stores structure
✅ Vue Router with 10 routes
✅ API service layer
✅ TypeScript type definitions
✅ Empty view components

## Next Steps

- Phase 2: Implement Mission Management UI
- Phase 3: Build Trust Scoring Dashboard
- Phase 4: Create PKI Management Interface
- Integrate Flask backend endpoints
- Add WebSocket real-time updates
- Implement Chart.js visualizations
