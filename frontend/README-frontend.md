# NewGenAI Financial Agent - Frontend

This is the Next.js 15 App Router frontend for the **NewGenAI Financial Agent** project (AI Guru 2026).

## Tech Stack
- **Framework**: Next.js 16.3 (App Router) + React 19
- **Language**: TypeScript
- **Styling**: Tailwind CSS v4, shadcn/ui
- **State Management**: Zustand (Client), TanStack Query (Server/API)
- **Animation**: Framer Motion
- **Icons**: Lucide React

## Folder Structure
- `src/app`: Routing, Pages, Layouts, Error boundaries
- `src/components/layout`: Global Layout (Sidebar, Topbar, AppLayout, RightPanel)
- `src/components/common`: Reusable UI components (MetricCard, etc.)
- `src/components/ui`: shadcn/ui primitives
- `src/features`: Domain-specific chunks (e.g. `chat/`, `parser/`)
- `src/providers`: Theme and Query providers
- `src/store`: Global Zustand stores
- `src/lib`: Utilities

## Getting Started

### Prerequisites
- Node.js >= 20
- npm (locked via `package-lock.json`)

### Installation
```bash
cd frontend
npm install
```

### Running Locally
```bash
npm run dev
```

Visit `http://localhost:3000` to view the Dashboard.
