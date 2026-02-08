# Agent Memory Playground - Frontend

Modern, minimalist dark mode frontend for testing AI agent memory strategies.

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Open http://localhost:3000
```

**Important:** Start the backend before the frontend. You can start it **from the frontend folder**:

```bash
# Option 1: npm script (from frontend/)
npm run backend

# Option 2: shell script (from frontend/)
./run-backend.sh
```

Or from the project root: `python api.py`. Backend runs on `http://localhost:8000`.

## Features

### Core Functionality
- **Dual Agent Comparison**: Run two agents side-by-side with different memory strategies
- **9 Memory Strategies**: Sequential, Sliding Window, Summarization, RAG, Compression, Hierarchical, Memory-Augmented, Graph, OS Paging
- **Real-time API Integration**: Live connection to FastAPI backend
- **Performance Metrics**: Track retrieval time, generation time, and token usage

### UI/UX
- **Dark Mode Minimalist Design**: Dark slate with light purple (violet) accents
- **Glassmorphism Effects**: Subtle backdrop blur on panels
- **Responsive Layout**: Works on mobile, tablet, and desktop
- **Keyboard Shortcuts**:
  - `Cmd/Ctrl + Enter` - Send message
  - `Cmd/Ctrl + K` - Clear memory
  - `Cmd/Ctrl + /` - Focus input

### Configuration
- **Memory Strategy Selection**: Choose from 9 different strategies per agent
- **Model Selection**: GPT-4o Mini, GPT-4o, GPT-4 Turbo, Claude 3.5 Sonnet
- **Advanced Parameters**: Temperature, max tokens, memory window size
- **System Prompt Customization**: Define custom agent personas
- **Sync Messages**: Send same message to both agents for comparison

## Tech Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: TailwindCSS v3 with custom dark theme
- **Icons**: Lucide React
- **State**: React hooks (useState, useEffect, useCallback)

## Project Structure

```
frontend/
├── app/
│   ├── page.tsx              # Root page component
│   ├── layout.tsx            # App layout with fonts
│   └── globals.css           # Global styles and scrollbar
├── components/
│   ├── playground.tsx        # Main playground component
│   ├── agent-window.tsx      # Agent chat interface
│   ├── config-panel.tsx      # Configuration sidebar
│   ├── glass-panel.tsx       # Reusable glass card
│   ├── memory-stats-panel.tsx # Performance metrics
│   ├── loading-indicator.tsx # Loading spinner
│   └── strategy-badge.tsx    # Strategy indicator
├── lib/
│   ├── types.ts              # TypeScript interfaces
│   ├── utils.ts              # Utility functions
│   └── api.ts                # Backend API client
├── package.json              # Dependencies
├── tsconfig.json             # TypeScript config
├── tailwind.config.ts        # Tailwind theme
├── next.config.js            # Next.js config
├── postcss.config.js         # PostCSS config
└── .env.local                # Environment variables
```

## Environment Variables

Create `.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Color Palette

Dark mode minimalist theme:

```typescript
slate: {
  950: '#020617', // body background
  900: '#0f172a', // panel background
  800: '#1e293b', // elevated surface
  700: '#334155', // borders
  600: '#475569', // subtle borders
  500: '#64748b', // tertiary text
  400: '#94a3b8', // placeholder
  300: '#cbd5e1', // secondary text
  100: '#f1f5f9', // primary text
}

violet: {
  600: '#8b5cf6', // primary accent
  500: '#a78bfa', // lighter purple
  400: '#c4b5fd', // active state
}
```

## API Integration

The frontend communicates with the FastAPI backend via REST endpoints:

- `GET /api/strategies` - Fetch available strategies
- `POST /api/agent/create` - Initialize agent with strategy
- `POST /api/chat` - Send message and get response
- `GET /api/agent/{id}/stats` - Get memory statistics
- `POST /api/agent/{id}/clear` - Clear agent memory
- `DELETE /api/agent/{id}` - Delete agent instance

## Development

### Install Dependencies

```bash
npm install
```

### Run Development Server

```bash
npm run dev
```

Visit [http://localhost:3000](http://localhost:3000)

### Build for Production

```bash
npm run build
npm start
```

### Lint

```bash
npm run lint
```

## Usage

1. **Start the backend** (from project root, not from `frontend/`): `python api.py` (port 8000)
2. **Start the frontend**: `npm run dev` (port 3000)
3. **Configure agents**: Select memory strategies and models
4. **Send messages**: Type and send to either or both agents
5. **Compare results**: See how different strategies handle the conversation
6. **Monitor performance**: Check retrieval time, generation time, and tokens

## Keyboard Shortcuts

- **Cmd/Ctrl + Enter**: Send message from focused input
- **Cmd/Ctrl + K**: Clear agent memory
- **Cmd/Ctrl + /**: Focus message input

## Troubleshooting

### Backend Connection Issues

If you see "Backend offline" error:
1. Check that the backend is running on port 8000
2. Verify `.env.local` has correct API URL
3. Check browser console for CORS errors

### Build Errors

If you encounter TypeScript errors:
```bash
rm -rf .next
npm run build
```

### Module Not Found

If imports fail:
```bash
rm -rf node_modules
npm install
```

## Performance

- Initial load: ~500ms
- Agent initialization: ~1-2s per agent
- Message response: ~2-4s (depends on LLM)
- Memory retrieval: <100ms

## Browser Support

- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support
- Mobile browsers: ✅ Responsive design

## Contributing

The frontend is built with modern React patterns:
- Functional components with hooks
- TypeScript for type safety
- Custom hooks for logic separation
- Memoization for performance

## License

MIT
