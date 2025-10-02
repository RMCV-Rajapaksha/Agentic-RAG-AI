# WSO2 AI Assistant - React Frontend

A modern React/TypeScript frontend for the WSO2 AI Assistant with Google OAuth authentication.

## Features

- 🔐 **Google OAuth Authentication** - Secure sign-in with Google accounts
- 💬 **Real-time Chat Interface** - Modern chat UI with message history
- 🎨 **Beautiful UI** - Built with Tailwind CSS and shadcn/ui components
- 📱 **Responsive Design** - Works seamlessly on desktop and mobile
- 🚀 **Fast Performance** - Powered by Vite and React 18
- 🔒 **Secure API Integration** - JWT token-based authentication with backend

## Prerequisites

- Node.js 18+ 
- npm or yarn or bun
- Google OAuth 2.0 Client ID
- Running WSO2 AI Assistant Backend API

## Setup Instructions

### 1. Install Dependencies

```bash
npm install
# or
yarn install
# or 
bun install
```

### 2. Configure Google OAuth

1. Go to [Google Cloud Console](https://console.developers.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Sign-In API
4. Go to Credentials → Create Credentials → OAuth 2.0 Client ID
5. Configure authorized origins:
   - `http://localhost:5173` (for development)
   - Your production domain
6. Copy the Client ID

### 3. Update Configuration

Edit `src/config/auth.ts`:

```typescript
export const GOOGLE_CLIENT_ID = "your-actual-client-id.apps.googleusercontent.com";
export const API_BASE_URL = "http://127.0.0.1:8000"; // Update if different
```

Also update `index.html`:

```html
<meta name="google-signin-client_id" content="your-actual-client-id.apps.googleusercontent.com">
```

### 4. Start Development Server

```bash
npm run dev
# or
yarn dev
# or
bun dev
```

The application will be available at `http://localhost:5173`

### 5. Backend Setup

Make sure your WSO2 AI Assistant backend is running and configured to:
- Accept requests from your frontend domain
- Validate Google JWT tokens
- Return responses in the expected format

## Project Structure

```
src/
├── components/
│   ├── ui/                 # shadcn/ui components
│   ├── ChatInterface.tsx   # Main chat interface
│   └── LoginPage.tsx       # Google sign-in page
├── contexts/
│   └── AuthContext.tsx     # Authentication context
├── config/
│   └── auth.ts            # Authentication configuration
├── types/
│   └── google.d.ts        # Google Sign-In type definitions
├── pages/
│   ├── Index.tsx          # Main page with auth routing
│   └── NotFound.tsx       # 404 page
└── lib/
    └── utils.ts           # Utility functions
```

## Authentication Flow

1. User visits the application
2. If not authenticated, shows Google Sign-In page
3. User signs in with Google account
4. JWT token is stored in localStorage
5. User can access the chat interface
6. API requests include the JWT token in Authorization header
7. User can sign out to clear authentication

## API Integration

The frontend expects the backend API to:

### Accept Authentication Header
```
Authorization: Bearer <google-jwt-token>
```

### POST /ask Endpoint
```json
{
  "query": "user question",
  "variables": {}
}
```

### Response Format
```json
{
  "answer": "AI response text",
  "url": ["optional", "reference", "urls"]
}
```

## Building for Production

```bash
npm run build
# or
yarn build
# or
bun run build
```

The built files will be in the `dist/` directory.

## Environment Variables

For production deployment, consider using environment variables:

```bash
VITE_GOOGLE_CLIENT_ID=your-client-id
VITE_API_BASE_URL=https://your-api-domain.com
```

Then update `src/config/auth.ts`:

```typescript
export const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || "fallback-client-id";
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
```

## Troubleshooting

### Google Sign-In Issues
- Verify your Client ID is correct
- Check that your domain is added to authorized origins
- Ensure the Google Sign-In script is loading properly

### API Connection Issues
- Verify the backend is running on the configured URL
- Check CORS settings on the backend
- Verify JWT token validation on the backend

### Build Issues
- Clear node_modules and reinstall dependencies
- Check for TypeScript errors
- Verify all imports are correct

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is part of the WSO2 AI Assistant application.
