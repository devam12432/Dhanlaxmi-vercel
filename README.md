# Angel One Invoice Generator — Vercel deployment

## Vercel
This project uses Vercel Services with two services in one project:
- `frontend/` — Vite React frontend
- `backend/` — Flask API

The root `vercel.json` routes `/api/*` to Flask and all other paths to the Vite frontend.

### Deploy
1. Push the contents of this folder to the root of your GitHub repository.
2. Import the repository into Vercel.
3. Keep Root Directory as `./`.
4. Vercel should show the configured Services from `vercel.json`; do not import `backend` or `frontend` as separate projects.
5. Deploy.
6. Test `https://YOUR-DOMAIN/api/health`; it should return `{"status":"ok"}`.

## Important
SQLite is stored under `/tmp` on Vercel because the deployment filesystem is not persistent. Use a persistent database for permanent production invoice history.
