# Domain Company Finder

A service that analyzes domains to find company names and contact information by scraping privacy policies and terms of service pages.

## Features

- Analyzes domains to extract company names
- Finds contact page URLs
- Simple API for managing domains
- In-memory database for Railway deployment
- Automatic periodic processing

## API Endpoints

- `GET /` - Info about the API
- `GET /api/domains` - List all domains
- `POST /api/domains` - Add a new domain
- `GET /api/domains/<domain>` - Get info for a specific domain
- `PUT /api/domains/<domain>` - Update a domain
- `DELETE /api/domains/<domain>` - Delete a domain
- `GET /healthz` - Health check endpoint

## Deployment to Railway

### Prerequisites

1. [Create a Railway account](https://railway.app/login)
2. Install the [Railway CLI](https://docs.railway.app/develop/cli)
3. Push this code to GitHub

### Deployment Steps

#### Option 1: Deploy using GitHub

1. Log in to [Railway Dashboard](https://railway.app/dashboard)
2. Click "New Project" and select "Deploy from GitHub repo"
3. Select your GitHub repository
4. Railway will automatically detect and deploy your project
5. Set the environment variable `ENABLE_WORKER=true` in Railway dashboard

#### Option 2: Deploy using Railway CLI

1. Open your terminal and navigate to the project directory
2. Log in to Railway:
   ```
   railway login
   ```
3. Link the project to Railway:
   ```
   railway init
   ```
4. Deploy the project:
   ```
   railway up
   ```
5. Set environment variables:
   ```
   railway variables set ENABLE_WORKER=true
   ```

### Checking Deployment Status

1. Go to the Railway dashboard
2. Select your project
3. Click on the "Deployments" tab to see the status of your deployment
4. Once deployed, click on "Generate Domain" to get a public URL for your API

## Local Development

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the app:
   ```
   ENABLE_WORKER=true python app.py
   ```

3. Test the API:
   ```
   python add_domain.py
   ```