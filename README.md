# Mane - Hair Care Shop

deployment Link - https://neusearch-ei5c888y3-vandit98s-projects.vercel.app/

An e-commerce platform with an AI-powered shopping assistant that helps users find the right hair care products.

## What it does

- **Product Catalog**: Browse 48+ hair care products scraped from Traya.health
- **AI Chat Assistant**: Ask questions like "I have dry scalp, what should I use?" and get personalized recommendations
- **Product Details**: View full product info including price, description, and features

## Tech Stack

- **Frontend**: React + TypeScript + Vite
- **Backend**: FastAPI + PostgreSQL (Supabase)
- **AI**: Google Gemini for chat and embeddings
- **Search**: pgvector for semantic product search

## Quick Start

### 1. Clone and setup backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Add your credentials
echo "DATABASE_URL=your_supabase_url" > .env
echo "GEMINI_API_KEY=your_gemini_key" >> .env

# Run
uvicorn app.main:app --reload --port 8000
```

### 2. Setup frontend

```bash
cd frontend
npm install
npm run dev
```

### 3. Load products

```bash
curl -X POST http://localhost:8000/api/scraper/run
```

Open http://localhost:3000

## How the RAG works

1. User asks a question
2. System searches products using text matching (or vector search if embeddings are available)
3. Relevant products are sent to Gemini as context
4. Gemini generates a helpful response with product recommendations

## API

| Endpoint | Description |
|----------|-------------|
| `GET /api/products` | List products |
| `GET /api/products/:id` | Get product |
| `POST /api/chat` | Chat with assistant |
| `POST /api/scraper/run` | Scrape products |

## Scraping

Products are fetched from Traya.health's Shopify API (`/products.json`). This gives us structured JSON data directly - no HTML parsing needed.

## Folder Structure

```
backend/
  app/
    api/        # Routes
    models/     # Database models
    services/   # Business logic
    scraper/    # Product scraper

frontend/
  src/
    components/ # UI components
    pages/      # Page views
    services/   # API calls
```

## Problem i faced 
The Render free tier only provides 512 MB RAM, which isn’t enough to load the sentence-transformers model (it requires ~800 MB with PyTorch).
So instead, I use an LLM to handle the conversation and then generate the recommended product.

Locally, the suggestion workflow creates an embedding of the user’s query, refines the query, and then performs a semantic similarity match between embeddings to identify the top 3 results.


## Screenshot
<img width="1500" height="689" alt="image" src="https://github.com/user-attachments/assets/5d57ea6c-74b9-4d19-a73b-84248a8594a5" />
<img width="1273" height="301" alt="image" src="https://github.com/user-attachments/assets/8a01fa62-c063-4c64-b489-646a07482a9c" />

<img width="1500" height="689" alt="image" src="https://github.com/user-attachments/assets/cd3599c7-a3b0-49fe-acd7-3dd0b09b1f5e" />
<img width="1500" height="890" alt="image" src="https://github.com/user-attachments/assets/0c23ac83-76d1-4324-9bfd-ac889ef06ead" />

