# Auto Reviewer v0.1

A full-stack application for automated content review using AI. The application features a React frontend with two markdown editors and a FastAPI backend that processes content through AI models.

## Project Structure

```
auto-reviewer/
├── front/                 # React frontend
│   ├── src/
│   │   ├── components/    # UI components
│   │   ├── lib/          # Utility functions
│   │   └── App.tsx       # Main application
│   ├── package.json
│   └── ...
├── back/                  # FastAPI backend
│   ├── main.py           # Main API server
│   ├── gcp.py            # GCP AI integration
│   └── requirements.txt  # Python dependencies
├── start-dev.sh          # Development startup script
└── README.md
```

## Features

- **Dual Markdown Editors**: Two side-by-side markdown editors for input and output
- **AI-Powered Review**: Backend integration with Google Cloud AI for content processing
- **Modern UI**: Built with React, TypeScript, and shadcn/ui components
- **Real-time Processing**: Fast API responses with streaming capabilities
- **Responsive Design**: Works on desktop and mobile devices

## Prerequisites

- Node.js (v16 or higher)
- Python (v3.8 or higher)
- npm or yarn

## Quick Start

### Option 1: Automated Setup (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd auto-reviewer
```

2. Run the development startup script:
```bash
./start-dev.sh
```

This script will:
- Install frontend dependencies
- Install backend dependencies
- Start both servers automatically
- Open the application in your browser

### Option 2: Manual Setup

#### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd front
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

#### Backend Setup

1. Navigate to the backend directory:
```bash
cd back
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Start the backend server:
```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at `http://localhost:8000`

## Usage

1. Open your browser and navigate to `http://localhost:3000`
2. Enter content in the left markdown editor
3. Click the play button in the center to process the content
4. View the reviewed content in the right markdown editor

## API Endpoints

- `GET /` - Health check
- `GET /health` - API status
- `POST /api/review` - Process content for review

### Review API Example

```bash
curl -X POST "http://localhost:8000/api/review" \
     -H "Content-Type: application/json" \
     -d '{"content": "Your content here"}'
```

## Development

### Frontend Development

The frontend is built with:
- React 18 with TypeScript
- Vite for fast development
- Tailwind CSS for styling
- shadcn/ui for components
- React Markdown Editor for content editing

### Backend Development

The backend is built with:
- FastAPI for the web framework
- Pydantic for data validation
- Google Cloud AI integration (GCP class)
- CORS middleware for frontend communication

## Environment Variables

Create a `.env` file in the backend directory for GCP configuration:

```env
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=global
```

## Contributing

1. Create a feature branch from main
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## License

This project is licensed under the MIT License.