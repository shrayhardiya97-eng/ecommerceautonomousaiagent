# Production Deployment Guide: E-Commerce Autonomous AI Shopping Agent

This guide walks you step-by-step through taking your **FastAPI Backend**, **Next.js Frontend**, **PostgreSQL Database**, **Qdrant Vector DB**, and **Shopify Storefront Integration** 100% LIVE on the internet.

---

## 🏗️ Architecture Summary

```
┌─────────────────────────────────────────────────────────────┐
│                    Customer Browser / Mobile                │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTPS
                               ▼
┌─────────────────────────────────────────────────────────────┐
│              Frontend (Next.js 14 on Vercel)                │
│    - Global CDN Edge Hosting                                │
│    - Domain: https://your-shopping-agent.vercel.app         │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTPS / JSON REST
                               ▼
┌─────────────────────────────────────────────────────────────┐
│              Backend (FastAPI on Render / AWS ECS)          │
│    - LangGraph Multi-Agent Pipeline                         │
│    - Security Headers, Rate Limiter, Prompt Guard           │
│    - Endpoint: https://ecommerce-ai-agent-backend.onrender.com
└───────┬──────────────────────┬──────────────────────┬───────┘
        │                      │                      │
        ▼                      ▼                      ▼
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│  PostgreSQL  │       │ Qdrant Cloud │       │ Shopify API  │
│  (Supabase / │       │  (Managed    │       │  (Storefront │
│    Render)   │       │  Vector DB)  │       │    GraphQL)  │
└──────────────┘       └──────────────┘       └──────────────┘
```

---

## Step 1: Git Repository Setup & Push to GitHub

1. Open PowerShell and navigate to your project directory:
   ```powershell
   cd C:\Users\LENOVO\.gemini\antigravity\scratch\ecommerce-agent
   ```

2. Initialize the Git repository (if not already done):
   ```powershell
   git init
   git branch -M main
   ```

3. Create a new repository on your GitHub account (`shrayhardiya97-eng`), named e.g.:
   `ecommerce-autonomous-ai-agent`

4. Add remote and push:
   ```powershell
   git remote add origin https://github.com/shrayhardiya97-eng/ecommerce-autonomous-ai-agent.git
   git add .
   git commit -m "feat: complete production-ready autonomous e-commerce ai shopping agent"
   git push -u origin main
   ```

---

## Step 2: Database Setup (PostgreSQL)

You can choose either **Render Managed PostgreSQL** or **Supabase**:

### Option A: Render Managed PostgreSQL (Recommended for 1-Click with Backend)
1. In Render Dashboard ([dashboard.render.com](https://dashboard.render.com)):
2. Click **New +** -> **PostgreSQL**.
3. Name it `ecommerce-agent-db`.
4. Copy the **Internal Database URL** (for Render backend) or **External Database URL**.

### Option B: Supabase (Free PostgreSQL)
1. Go to [supabase.com](https://supabase.com) and create a free project.
2. Under **Project Settings** -> **Database**, copy the **URI Connection String**.
3. In Supabase SQL Editor, paste and run the contents of [`app/db/migrations.sql`](file:///C:/Users/LENOVO/.gemini/antigravity/scratch/ecommerce-agent/app/db/migrations.sql) to provision tables.

---

## Step 3: Vector Database Setup (Qdrant Cloud)

1. Sign up for free at [cloud.qdrant.io](https://cloud.qdrant.io).
2. Create a **Free Tier Cluster** (1GB RAM, 0.5 vCPU).
3. Under Cluster details, copy:
   - **Cluster URL** (e.g., `https://xyz-your-cluster.qdrant.tech:6333`)
   - **API Key** (Generate under *API Keys*)

*(Note: If you leave `QDRANT_URL` blank, the agent automatically falls back to its internal zero-dependency dense vector cosine similarity engine, guaranteeing 100% uptime).*

---

## Step 4: Backend Deployment (Render)

1. Go to [dashboard.render.com](https://dashboard.render.com) -> **New +** -> **Blueprint**.
2. Select your repository `shrayhardiya97-eng/ecommerce-autonomous-ai-agent`.
3. Render will automatically read [`render.yaml`](file:///C:/Users/LENOVO/.gemini/antigravity/scratch/ecommerce-agent/render.yaml) and configure:
   - Web Service: `ecommerce-ai-agent-backend`
   - Database: `ecommerce-agent-db`
4. Set the following Environment Variables in the Render dashboard:
   - `OPENAI_API_KEY`: Your OpenAI API key (from [platform.openai.com](https://platform.openai.com))
   - `SHOPIFY_SHOP_URL`: `your-store.myshopify.com`
   - `SHOPIFY_ACCESS_TOKEN`: Your Storefront or Admin API access token
   - `USE_MOCK_SHOPIFY`: `False` (to use live Shopify API) or `True` (for the verified mock catalog)
   - `QDRANT_URL`: Your Qdrant Cloud URL
   - `QDRANT_API_KEY`: Your Qdrant Cloud API Key
   - `CORS_ALLOWED_ORIGINS`: `*` or your Vercel frontend URL
5. Click **Apply**.
6. When deployment finishes, copy your live backend URL (e.g. `https://ecommerce-ai-agent-backend.onrender.com`).
7. Test the health endpoint:
   `https://ecommerce-ai-agent-backend.onrender.com/health`

---

## Step 5: Frontend Deployment (Vercel)

1. Go to [vercel.com](https://vercel.com) -> Click **Add New...** -> **Project**.
2. Import your GitHub repository: `shrayhardiya97-eng/ecommerce-autonomous-ai-agent`.
3. Set **Root Directory** to `frontend`.
4. Under **Environment Variables**, add:
   - Key: `NEXT_PUBLIC_API_URL`
   - Value: `https://ecommerce-ai-agent-backend.onrender.com` (your live Render backend URL)
5. Click **Deploy**.
6. Vercel will build the Next.js app and assign a live production URL (e.g. `https://ecommerce-ai-agent.vercel.app`).

---

## Step 6: Shopify Storefront API Credentials

To connect a live Shopify store:
1. Open your Shopify Admin (`https://admin.shopify.com/store/{your-store}`).
2. Go to **Settings** -> **Apps and sales channels** -> **Develop apps**.
3. Click **Create an app** -> Name it `Autonomous AI Agent`.
4. Under **Configuration**, grant:
   - **Storefront API access scopes**: `unauthenticated_read_product_listings`, `unauthenticated_read_product_inventory`, `unauthenticated_write_checkouts`, `unauthenticated_read_checkouts`.
5. Under **API credentials**, install the app and copy the **Storefront API access token**.
6. Add this token as `SHOPIFY_ACCESS_TOKEN` in your Render backend settings.

---

## Step 7: CI/CD Pipeline (GitHub Actions)

To enable automatic zero-downtime deployments on `git push origin main`:
1. In your GitHub repository, go to **Settings** -> **Secrets and variables** -> **Actions**.
2. Add the following secrets:
   - `RENDER_DEPLOY_HOOK_URL`: (Obtained from Render Web Service -> Settings -> Deploy Hook)
   - `VERCEL_TOKEN`: (From Vercel Account Settings -> Tokens)
   - `VERCEL_ORG_ID`: (From `.vercel/project.json` or team settings)
   - `VERCEL_PROJECT_ID`: (From Vercel Project Settings)
   - `LIVE_BACKEND_URL`: `https://ecommerce-ai-agent-backend.onrender.com`

---

## Step 8: Live End-to-End Verification Checklist

Once both frontend and backend are live:
1. [ ] **Health Probe:** Visit `https://your-backend.onrender.com/health` -> Ensure `status: "healthy"`.
2. [ ] **Storefront Loading:** Open `https://your-frontend.vercel.app`.
3. [ ] **Query Discovery:** Type: *"I need a laptop under ₹70,000 for programming, machine learning, and gaming."*
4. [ ] **Intent Check:** Verify agent recognizes Budget (₹70,000), Category (Laptop), Specs (GPU CUDA, 16GB RAM).
5. [ ] **Comparison:** Switch to *Side-by-Side Comparison* tab to view the spec matrix.
6. [ ] **Stock Verification:** Check the live stock badge on product cards.
7. [ ] **Cart Operations:** Click *Add to Cart* on the top pick.
8. [ ] **HITL Security Gate:** Click *Proceed to Secure Review*.
9. [ ] **Customer Confirmation:** Check the authorization box and click *Authorize & Open Shopify Checkout*.
10. [ ] **Shopify Redirection:** Confirm redirection to the authentic Shopify checkout permalink.
