# AI Resume Report Frontend

This folder contains a React-based dashboard built with Vite. It lives independently from the backend logic so the rest of the project is not affected.

The dashboard uses Material‑UI for layout and styling, Recharts for charts, and Axios for future API calls. It currently shows a **Home** page where users can paste resume text or upload a file, plus a placeholder "User Growth" chart and a basic sidebar/navigation structure with routes. React Router handles navigation between sections.

## Getting started

1. **Install dependencies**
   ```powershell
   cd frontend
   npm install
   ```

2. **Run development server**
   ```powershell
   npm run dev
   ```

   Visit `http://localhost:5173` (or the URL output by Vite) in your browser.

3. **Build for production**
   ```powershell
   npm run build
   ```

4. **Lint the code**
   ```powershell
   npm run lint
   ```

Feel free to expand the dashboard by adding pages, charts, or hooking it up to the Python backend with Axios.

## Backend API

A simple FastAPI server (`backend.py`) exposes endpoints for analysis:

- `POST /api/analyze` accepts JSON `{ inputType, value }` where `inputType` is
  "text" or "documentation" and `value` is the resume text or documentation URL.
- `POST /api/upload` accepts a file upload (e.g. resume file) and returns a skill list.

Start the backend by installing the Python requirements and running:

```powershell
pip install -r requirements.txt
python backend.py            # or: uvicorn backend:app --reload --port 8000
```

Ensure the AI API key (e.g. `GROQ_API_KEY`) is set if you want real analysis.
The frontend calls these endpoints automatically using Axios when you submit input.

