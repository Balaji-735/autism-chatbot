# Autism Chatbot Frontend

A modern Next.js 14 frontend for the Autism Chatbot RAG system.

## Features

- 🚀 Next.js 14 with App Router
- 📱 Responsive design with Tailwind CSS
- 🎨 Beautiful UI with shadcn/ui components
- 💬 Real-time chat interface
- 📄 Source citations for answers
- ⚡ Fast and optimized

## Prerequisites

- Node.js 18+ and npm/yarn
- Backend API server running on port 8000 (default)

## Installation

1. Install dependencies:
```bash
npm install
```

2. Create a `.env.local` file:
```bash
cp .env.example .env.local
```

3. Update `.env.local` with your API URL if different:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Development

Run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Build

Build for production:

```bash
npm run build
```

Start the production server:

```bash
npm start
```

## Project Structure

```
frontend/
├── app/                # Next.js App Router
│   ├── layout.tsx     # Root layout
│   ├── page.tsx       # Main chat page
│   └── globals.css    # Global styles
├── components/         # React components
│   └── ui/            # shadcn/ui components
├── lib/               # Utilities and API client
│   ├── api.ts         # API client functions
│   └── utils.ts       # Utility functions
└── public/            # Static assets
```

## API Integration

The frontend communicates with the FastAPI backend at `/api/query` endpoint. Make sure the backend server is running before starting the frontend.


