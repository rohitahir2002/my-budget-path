# 🚀 Vercel Deployment Guide for BudgetPath Pro
### Full-Stack AI Budget Planner (FastAPI + MongoDB Atlas + Glassmorphic UI)

This guide walks you step-by-step through deploying your entire **BudgetPath Pro** project to **Vercel** with zero hassle.

---

## 📋 Architecture on Vercel

```
                        ┌──────────────────────────────────────────┐
                        │      Your Vercel Deployment URL          │
                        │    (e.g., https://budgetpath.vercel.app) │
                        └─────────────────────┬────────────────────┘
                                              │
                      ┌───────────────────────┴───────────────────────┐
                      ▼                                               ▼
          Frontend Routes (/, /*)                         Backend API (/api/*, /docs)
          Served via Vercel CDN                           Executed as Serverless Function
          (Frontend/index.html)                           (api/index.py ➔ FastAPI app)
                      │                                               │
                      │                                               ▼
                      └────────── Same-Origin API Calls ────────── MongoDB Atlas Cluster
                                 (No CORS configuration needed!)   (cluster0.onhvcjv.mongodb.net)
```

---

## 🔑 Phase 1: MongoDB Atlas Configuration (Important!)

Because Vercel serverless functions run in dynamically assigned cloud IPs, MongoDB Atlas must allow connections from any IP.

1. Go to [cloud.mongodb.com](https://cloud.mongodb.com) and log in.
2. In the left sidebar, click **Network Access** (under the *Security* section).
3. Check the IP Access List:
   - If you do not see `0.0.0.0/0`, click **+ Add IP Address**.
   - Click **Allow Access from Anywhere** (adds `0.0.0.0/0`).
   - Click **Confirm**. (Status will turn to *Active* within 1-2 minutes).
4. Verify your Database User:
   - Click **Database Access** in the left sidebar.
   - Ensure your database user (e.g., `workrohitahir_db_user`) has `Read and write to any database` privileges.
5. Your MongoDB connection string:
   ```text
   mongodb+srv://workrohitahir_db_user:km40XNgjQLujxBe0@cluster0.onhvcjv.mongodb.net/?retryWrites=true&w=majority
   ```

---

## 🚀 Phase 2: Deploy to Vercel via GitHub (Recommended)

### Step 1: Commit and Push to GitHub

In your VS Code terminal or PowerShell:

```powershell
# 1. Stage the new files and updates
git add .

# 2. Commit the changes
git commit -m "Configure project for Vercel serverless deployment"

# 3. Push to your GitHub branch
git push origin development
```

*(If you are deploying from your `main` branch, merge or push to `main`).*

---

### Step 2: Import Project on Vercel

1. Go to [vercel.com](https://vercel.com) and log in (using your GitHub account).
2. Click **Add New...** at the top right, then select **Project**.
3. Under **Import Git Repository**, find your repository:
   - **`rohitahir2002/my-budget-path`**
   - Click **Import**.

---

### Step 3: Configure Project Settings on Vercel

On the **Configure Project** screen:

1. **Project Name**: Keep as `my-budget-path` (or customize as desired).
2. **Framework Preset**: Select **Other**.
3. **Root Directory**: Leave as `./` (Root).
4. **Environment Variables**: Expand the **Environment Variables** section and add the following 3 variables:

| Variable Name | Value | Purpose |
| :--- | :--- | :--- |
| `MONGO_URI` | `mongodb+srv://workrohitahir_db_user:km40XNgjQLujxBe0@cluster0.onhvcjv.mongodb.net` | Atlas Connection URI |
| `DB_NAME` | `budgetpath` | Database name |
| `JWT_SECRET_KEY` | `budgetpath_super_secret_jwt_key_2026_secure_key_change_in_production` | JWT Auth Signature Key |

> 💡 **Tip**: You can copy-paste all 3 directly into Vercel using the raw text box or add them one by one.

5. Click **Deploy**! 🚀

---

### Step 4: Watch Deployment Complete

Vercel will:
- Automatically detect the Python runtime (`@vercel/python`).
- Read [requirements.txt](file:///c:/Users/Rohit%20Ahir/OneDrive/Desktop/College%20Project/requirements.txt) and install `fastapi`, `motor`, `pymongo`, `bcrypt`, `certifi`, etc.
- Build the static Frontend.
- Deploy in ~60-90 seconds.

Once complete, Vercel will provide your live URL (e.g., `https://my-budget-path.vercel.app`).

---

## 💻 Alternative: Deploying via Vercel CLI

If you prefer deploying directly from your computer terminal without going through the web UI:

```powershell
# 1. Install Vercel CLI globally
npm install -g vercel

# 2. Login to Vercel
vercel login

# 3. Deploy to preview
vercel

# 4. Set Environment Variables
vercel env add MONGO_URI
vercel env add DB_NAME
vercel env add JWT_SECRET_KEY

# 5. Deploy to Production
vercel --prod
```

---

## 🔍 Phase 3: Post-Deployment Verification Checklist

Once your deployment is live at `https://<your-project>.vercel.app`:

### 1. Test Health & Database Connectivity
Open:
```
https://<your-project>.vercel.app/api/health
```
**Expected Response:**
```json
{
  "status": "healthy",
  "service": "BudgetPath API",
  "database": "connected"
}
```

### 2. Test Interactive Swagger API Documentation
Open:
```
https://<your-project>.vercel.app/docs
```
You will see the complete interactive OpenAPI documentation listing all endpoints (`/api/auth`, `/api/budget`, `/api/transactions`, `/api/history`, `/api/admin`).

### 3. Test Full-Stack Web App UI
Open:
```
https://<your-project>.vercel.app/
```
- The modern Glassmorphic FinTech UI will load instantly.
- Click **Sign In / Register** ➔ create an account.
- Add sample or live income/expenses ➔ watch the gauges, donuts, waterfall charts, and ML regression run live!
- Add transactions in the ledger ➔ view monthly statistics and category breakdowns.

---

## 🛠️ Summary of Files Created & Modified for Vercel

1. **[vercel.json](file:///c:/Users/Rohit%20Ahir/OneDrive/Desktop/College%20Project/vercel.json)**:
   - Configures URL rewrites: `/api/*` and `/docs` route to the FastAPI serverless function, while `/` and static assets route to `Frontend/index.html`.
2. **[api/index.py](file:///c:/Users/Rohit%20Ahir/OneDrive/Desktop/College%20Project/api/index.py)**:
   - Serverless entrypoint recognized by Vercel's Python runtime. It mounts the Backend FastAPI instance.
3. **[requirements.txt](file:///c:/Users/Rohit%20Ahir/OneDrive/Desktop/College%20Project/requirements.txt)**:
   - Contains clean, production-ready dependencies with `certifi` for SSL handshakes and pure `bcrypt`.
4. **[Backend/app/database.py](file:///c:/Users/Rohit%20Ahir/OneDrive/Desktop/College%20Project/Backend/app/database.py)**:
   - Upgraded with resilient lazy initialization (`init_db()`), ensuring that even during cold starts in serverless functions, MongoDB connection handles are cached and reconnect seamlessly.
5. **[Frontend/index.html](file:///c:/Users/Rohit%20Ahir/OneDrive/Desktop/College%20Project/Frontend/index.html)**:
   - Updated `API_BASE` to dynamically detect environment:
     - Local Live Server / static file: points to `http://localhost:8000/api`.
     - Vercel cloud: points automatically to relative `/api` (same origin).
6. **[.gitignore](file:///c:/Users/Rohit%20Ahir/OneDrive/Desktop/College%20Project/.gitignore)**:
   - Untracked binary `.exe` and local `.env` so secrets remain protected and deployments stay ultra-fast.
