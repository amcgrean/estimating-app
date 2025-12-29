# PA Bid Request - Deployment Guide

This guide explains how to deploy the application to GitHub and Vercel.

## 1. Prepare for GitHub
- Ensure your changes are committed.
- Ensure `instance/bids.db` and `.env` are listed in `.gitignore` (they should be already).
- Push your code to a GitHub repository.

## 2. Deploy to Vercel
- Import your GitHub repository in the [Vercel Dashboard](https://vercel.com).
- **Framework Preset**: Choose **Other** or **Flask** (it should auto-detect).
- **Environment Variables**:
  - `SECRET_KEY`: A long random string.
  - `PYTHON_VERSION`: `3.11`
- **Database**: Add **Vercel Postgres (Neon)** from the Storage tab.
  - When the **"Connect Project"** modal appeared (per your screenshot):
    - **Environments**: Keep "Production" and "Development" checked.
    - **Create Database Branch**: You can leave "Preview" and "Production" **unchecked** for now to keep it simple and use a single "main" branch.
    - **Custom Prefix**: Change `STORAGE` to `POSTGRES` (or `DATABASE`) so the variable names are more standard (e.g., `POSTGRES_URL`).
  - Click **Connect**. This will set the connection strings automatically in Vercel.

## 3. Migrate Your Data
Since you have existing data in `instance/bids.db`, run the migration script locally:

1. Install requirements: `pip install -r requirements.txt`
2. Get your `DATABASE_URL` from the Vercel Dashboard (Storage -> Postgres -> .env.local section).
3. Run the script:
   ```bash
   # On Windows (PowerShell):
   $env:DATABASE_URL="your-postgres-url-here"; python migrate_to_postgres.py
   
   # On Mac/Linux:
   DATABASE_URL="your-postgres-url-here" python migrate_to_postgres.py
   ```

## 4. Final Check
Once the migration is done, your Vercel-deployed application should have all your users, bids, and designs ready to go.
