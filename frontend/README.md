# ⚽ Football Player Management UI

A modern React 19 + TypeScript frontend for managing football players with real-time data sync.

---

## 🚀 Quick Start

### Local Development

```bash
cd frontend
npm install
npm run dev
```

- **App:** http://localhost:5173
- **Backend API:** http://localhost:8000 (must be running)

### Docker

```bash
# Build
docker build -t football-frontend .

# Run
docker run --rm -p 3000:3000 football-frontend
```

---

## 📁 Project Structure

```
src/
├── main.tsx                # React entry point
├── index.css               # Global styles
├── services/
│   ├── api.ts              # Axios HTTP client (baseURL = VITE_API_LOCATION)
│   └── index.ts            # Axios instance export
├── hooks/
│   ├── usePlayers.ts       # Server state (TanStack Query) + mutations
│   └── usePlayersView.ts   # UI state (modal, editing, deletion)
├── components/
│   ├── navbar/             # Navigation header
│   ├── playerHeader/       # Player list title & actions
│   ├── player/             # Individual player card
│   ├── playerFormModal/    # Create/Edit form modal
│   └── deleteConfirmModal/ # Delete confirmation dialog
├── pages/
│   ├── home/               # Home page
│   └── players/            # Players list page
├── layouts/
│   └── RootLayout.tsx      # App wrapper with navbar
├── routes/
│   └── routes.tsx          # React Router definitions
├── types/
│   └── index.ts            # TypeScript types & Zod schemas
└── utils/
    └── index.ts            # Helper functions
```

---

## 🔌 Backend Communication

The frontend communicates with the backend API via HTTP:

### Configuration Files

**`.env` (Local Development):**

```
VITE_API_LOCATION=http://127.0.0.1:8000
```

**`.env.production` (Docker):**

```
VITE_API_LOCATION=http://backend:8000
```

### API Service Layer

[services/api.ts](src/services/api.ts) exports:

- `getPlayers()` → `GET /players`
- `getPlayer(id)` → `GET /players/{id}`
- `createPlayer(data)` → `POST /players`
- `updatePlayer(id, data)` → `PUT /players/{id}`
- `deletePlayer(id)` → `DELETE /players/{id}`

### Custom Hooks

**`usePlayers`** — Server state management:

- `playersQuery` — Fetches all players
- `singlePlayerQuery` — Fetches single player for editing
- `createMutation` — Creates new player
- `updateMutation` — Updates player
- `deleteMutation` — Deletes player
- Auto-refetch after mutations

**`usePlayersView`** — UI state management:

- `isModalOpen` — Create/Edit form visibility
- `isDeleteConfirmOpen` — Delete confirmation visibility
- `editingId` — Currently editing player ID
- `deletingId` — Player pending deletion
- `openCreateModal`, `openEditModal`, `confirmDelete` — Event handlers

---

## 🎨 Component Architecture

```
RootLayout
  └── Navbar
    └── pages/
      ├── HomePage
      └── PlayersPage
          ├── PlayersHeader (title + create button)
          ├── StateViews (loading/error/empty states)
          ├── PlayerCard (individual player with edit/delete)
          ├── PlayerFormModal (create/edit form)
          └── DeleteConfirmModal (delete confirmation)
```

### Component Features

- **PlayerCard** — Shows player info, edit/delete buttons
- **PlayerFormModal** — Form validation with Zod, auto-fill for editing
- **DeleteConfirmModal** — Confirmation before deletion
- **StateViews** — Handles loading, error, and empty list states
- **All styled** — Component-scoped CSS files

---

## 📦 Tech Stack

- **React 19** — UI framework
- **TypeScript** — Type safety
- **Vite** — Build tool & dev server
- **TanStack Query** — Server state (fetch, cache, mutations)
- **React Router v6** — Client-side routing
- **Axios** — HTTP client
- **Zod** — Form validation & runtime type checking
- **ESLint** — Code quality

---

## 🔄 Data Flow

```
User Action (Click Create/Edit/Delete)
    ↓
usePlayersView (UI state)
    ↓
usePlayers (Server mutation: create/update/delete)
    ↓
api.ts (Axios HTTP request)
    ↓
Backend /players endpoint
    ↓
usePlayers (auto-refetch playersQuery)
    ↓
Component re-render with new data
```

---

## 📚 Available Commands

```bash
# Development
npm run dev          # Start dev server (port 5173)
npm run build        # Production build → dist/
npm run preview      # Preview production build
npm run lint         # Run ESLint

# Build & Deploy
npm run build        # Creates optimized bundle in dist/
# Then serve dist/ folder with any static server
```

---

## 🌍 Environment Variables

### Development (`.env`)

```
VITE_API_LOCATION=http://127.0.0.1:8000
```

### Production (`.env.production`)

```
VITE_API_LOCATION=http://backend:8000  # Docker Compose
# or
VITE_API_LOCATION=https://api.example.com  # Real API URL
```

**Note:** Frontend automatically uses correct env based on build mode.

---

## 🐛 Debugging

### React DevTools Browser Extension

- Chrome: [React Developer Tools](https://chrome.google.com/webstore)
- Firefox: [React Developer Tools](https://addons.mozilla.org/firefox)

### TanStack Query DevTools

Enabled in development mode — press `⌘`/`Ctrl` to toggle panel.

### Network Requests

1. Open Chrome DevTools (F12)
2. Go to **Network** tab
3. Perform player actions (create, edit, delete)
4. Click on request to see request/response details

---

## 🤖 AI Assistance

Prompts and focus areas:

- UI layout and component architecture best practices
- React + TypeScript patterns for state management and forms
- Consistent styling and UX for modals, lists, and empty states

Verification:

- Manual checks of CRUD flows, loading/error/empty states, and modal UX
- Linting with `npm run lint`

---

## 📄 License

MIT
