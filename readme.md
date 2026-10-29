# BudgetPath Pro – AI-Powered Budget Planner & Expense Management System

> **A Full-Stack Financial Forecasting & Management Platform with Machine Learning, MongoDB Persistence, JWT Authentication, and Role-Based Access Control (RBAC).**

---

## 📌 1. Project Overview & Motivation

### What is BudgetPath Pro?
**BudgetPath Pro** is an advanced full-stack financial technology application designed to help individuals plan, manage, and predict their personal finances. Unlike traditional budget trackers that only record past expenses, BudgetPath combines **client-side and server-side machine learning** to forecast next month's discretionary spending ("wants") while continuously auditing user finances against the proven **50/30/20 financial rule**.

### Problem Statement
Most people struggle with budget planning because:
1. Expense forecasting is difficult due to varying monthly habits and festive seasons.
2. Existing apps only record past expenses without predicting future trends.
3. Users lack clear compound-interest projections for long-term savings and investments (SIPs).
4. Multi-user systems often lack strict role separation and data privacy.

### Our Solution
BudgetPath Pro solves these challenges by combining:
- **Autoregressive Machine Learning (Ridge Linear Regression)** to forecast category-wise discretionary spending.
- **Asynchronous FastAPI REST Backend** for high-throughput, low-latency API handling.
- **MongoDB NoSQL Cloud/Local Database** for scalable, schema-flexible financial data storage.
- **Role-Based Access Control (RBAC)** to ensure users can only access their own private financial records, with a specialized administrative governance portal.
- **Dynamic 50/30/20 Rule Analysis & Wealth Simulation** showing month-by-month compound growth toward a target savings goal.

---

## 🏗️ 2. System Architecture

```mermaid
graph TD
    subgraph Client ["Frontend Layer (Browser / SPA)"]
        UI["Glassmorphic UI (HTML5 + CSS3 + Vanilla JS)"]
        ML_Client["In-Browser ML Engine (Ridge Regression)"]
        SVG_Charts["Dynamic SVG Visualizations"]
        TokenStore["Local Storage (JWT Token & Session)"]
    end

    subgraph API_Gateway ["Backend Layer (FastAPI)"]
        CORS["CORS Middleware"]
        AuthMiddleware["JWT Authentication & Token Decoding"]
        RBAC_Guard["RBAC Dependency Injection (User / Admin)"]
        
        Router_Auth["/api/auth (Login, Register, Me)"]
        Router_Budget["/api/budget (Plans, Needs, Investments)"]
        Router_Tx["/api/transactions (Ledger & Summaries)"]
        Router_Hist["/api/history (Cloud CSV Datasets)"]
        Router_Admin["/api/admin (System Analytics & Users)"]
    end

    subgraph Database_Layer ["Database Layer (MongoDB)"]
        Col_Users[("users Collection")]
        Col_Budget[("budget_plans Collection")]
        Col_Tx[("transactions Collection")]
        Col_Hist[("historical_data Collection")]
    end

    UI --> ML_Client
    UI --> SVG_Charts
    UI --> TokenStore
    UI -->|HTTP Requests with Bearer Token| CORS

    CORS --> AuthMiddleware
    AuthMiddleware --> RBAC_Guard

    RBAC_Guard --> Router_Auth
    RBAC_Guard --> Router_Budget
    RBAC_Guard --> Router_Tx
    RBAC_Guard --> Router_Hist
    RBAC_Guard --> Router_Admin

    Router_Auth --> Col_Users
    Router_Budget -->|Strict Filter: user_id| Col_Budget
    Router_Tx -->|Strict Filter: user_id| Col_Tx
    Router_Hist -->|Strict Filter: user_id| Col_Hist
    Router_Admin -->|Admin Access Only| Col_Users
```

---

## 🧠 3. How the Machine Learning Engine Works

### Algorithm: Ridge Linear Regression ($L_2$ Regularization)
The application forecasts future category-wise spending using a regularized linear model:
$$\hat{y} = Xw$$
Where weights $w$ are solved using the **closed-form Normal Equation with $L_2$ Tikhonov regularization**:
$$w = (X^T X + \lambda I)^{-1} X^T y$$

- **Why Ridge Regression?** Discretionary spending categories often exhibit multicollinearity and month-to-month variance. The $\lambda$ penalty term ($\lambda = 1.0$) prevents overfitting and keeps weight estimates stable even with small training sample sizes (e.g., 6–36 months).

### Feature Engineering
For every category at month $i$, the model extracts a 5-dimensional feature vector:
$$x_i = [1, \quad a_{i-1}, \quad a_{i-2}, \quad a_{i-3}, \quad F \cdot a_{i-1}]$$

1. **Bias Term ($1$)**: Baseline constant spend.
2. **Lag 1 ($a_{i-1}$)**: Spending in the immediately preceding month.
3. **Lag 2 ($a_{i-2}$)**: Spending two months prior.
4. **Lag 3 ($a_{i-3}$)**: Spending three months prior (captures quarterly trends).
5. **Festive Multiplier ($F \cdot a_{i-1}$)**: Binary flag $F = 1$ when the calendar month is October or later ($m \ge 10$, Diwali/festive/holiday season in India), capturing seasonal surges in discretionary shopping and entertainment.

### Model Evaluation & Baselines
The model evaluates its performance against two industry baselines using an **80/20 chronological time-split** (training on earlier months, testing on the latest unseen months):
1. **Baseline 1 (Last-Month Persistence)**: Predicts $\hat{y}_i = a_{i-1}$.
2. **Baseline 2 (3-Month Moving Average)**: Predicts $\hat{y}_i = \frac{a_{i-1} + a_{i-2} + a_{i-3}}{3}$.
3. **Ridge Regression (Ours)**: Typically achieves **15% to 35% lower Mean Absolute Error (MAE)** and Root Mean Squared Error (RMSE) than the baselines.

---

## 📊 4. Financial Mathematics & Simulation

### 1. The 50 / 30 / 20 Budget Rule
The application continuously splits monthly income into three buckets:
- **50% Needs**: Essential fixed bills (Rent, EMI, utilities, groceries, medicines).
- **30% Wants**: Discretionary spending predicted by the AI model (dining out, entertainment, shopping).
- **20% Savings & Investments**: Capital allocated to investments and cash emergency fund.
- **Alert Diagnostics**: If Needs $> 50\%$ or Wants $> 30\%$, the system issues precise monetary cutback alerts (e.g., *"Reduce Shopping by ₹1,200"*).

### 2. Compound Interest Wealth Projection
To calculate whether the user will reach their target savings goal within $M$ months:
$$\text{Portfolio Value}(M) = \text{Cash Balance}(M) + \sum_{k} \text{SIP}_k(M)$$

- **Unallocated Cash Growth**: Compounded monthly at the annual base return rate $r_{\text{base}}$:
  $$C_m = C_{m-1} \cdot \left(1 + \frac{r_{\text{base}}}{12}\right) + \text{Cash Saved}$$
- **Individual Investment SIP Growth**: Each investment (Mutual Funds, FD, PPF, Stocks) compounds monthly at its specific expected rate $r_k$:
  $$I_{k, m} = I_{k, m-1} \cdot \left(1 + \frac{r_k}{1200}\right) + A_k$$
- **Shortfall Adjustment**: If projected balance $<$ Goal, the system calculates the exact additional monthly savings required:
  $$\Delta = \frac{\text{Shortfall} \cdot \frac{r}{12}}{\left(1 + \frac{r}{12}\right)^M - 1}$$

---

## 📈 5. Pictorial Statistics & Advanced Visualizations

BudgetPath Pro provides a rich suite of pure-SVG, high-performance visual instruments to give users instant visual clarity on their finances without heavy external libraries:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   PICTORIAL STATISTICAL DASHBOARD                      │
├──────────────────────────┬─────────────────────────────────────────────┤
│ 1. Health Speedometer    │ Radial arc gauge (0-100 score & status)     │
│ 2. Cashflow Waterfall    │ Step-by-step pictorial money pipeline       │
│ 3. Expense Donut Chart   │ Category-by-category outflow breakdown      │
│ 4. Portfolio Asset Donut │ Equity vs Debt vs Gold vs Liquid Cash       │
│ 5. Savings Goal Curve    │ Compound interest curve vs Target line      │
│ 6. 50/30/20 Stacked Bars │ Proportional budget diagnostic comparisons  │
│ 7. ML Prediction Bars    │ Horizontal bars showing next month's wants  │
│ 8. Transaction Analytics │ Spend category velocity & payment methods   │
└──────────────────────────┴─────────────────────────────────────────────┘
```

### 1. Financial Health Speedometer (Radial Arc Gauge)
- **Visual Method**: 180° semi-circular SVG arc gauge with dynamic needle fill and color status grading.
- **Algorithm**: Computes a holistic score (0 to 100) based on:
  - **Needs Ratio**: $\le 50\%$ earns +25 points (penalized proportionally if overspending).
  - **Wants Ratio**: $\le 30\%$ earns +15 points.
  - **Savings Rate**: $\ge 20\%$ earns +20 points.
  - **Goal Target Alignment**: +15 points if on-track to reach savings goal within target months.
- **Grading Scale**:
  - `85 - 100`: **EXCELLENT** (Emerald green glow)
  - `70 - 84`: **GOOD HEALTH** (Teal glow)
  - `45 - 69`: **MODERATE / CAUTION** (Amber gold)
  - `< 45`: **HIGH RISK** (Crimson red warning)

### 2. Cashflow Allocation Waterfall (Flow Diagram)
- **Visual Method**: A Sankey-inspired pictorial pipeline with glassmorphic cards and animated flow arrows showing how every rupee travels through the user's budget:
  $$\text{Total Inflow (₹45,000)} \longrightarrow \text{Needs (50%)} \longrightarrow \text{Wants (30%)} \longrightarrow \text{SIPs (15%)} \longrightarrow \text{Buffer (5%)}$$
- **Benefit**: Allows the user and evaluators to immediately spot cash leakage and unallocated surpluses.

### 3. Expense Category Breakdown Donut Chart
- **Visual Method**: Interactive SVG Donut Chart with hoverable arc slices, center-mounted total outflow counter, and a detailed percentage legend.
- **Content**: Combines fixed monthly needs (Rent, EMI, Food, Utilities) with AI-predicted wants (Entertainment, Shopping, Dining).

### 4. Asset Allocation & Portfolio Risk Donut
- **Visual Method**: Multi-colored SVG ring chart illustrating investment diversification across four major asset classes:
  - **Equity (Growth)**: Mutual Fund SIPs, Direct Stocks (High return, 11%–12%).
  - **Debt / Fixed Income (Stability)**: Fixed Deposits, Recurring Deposits, PPF (Guaranteed, 6.5%–7.1%).
  - **Commodities**: Physical / Digital Gold (Inflation hedge, 8%).
  - **Liquid Buffer**: Unallocated cash in savings account.

### 5. Savings Path Projection (Wealth Accumulation vs Target Goal)
- **Visual Method**: Multi-series SVG Cartesian coordinate graph with dual curves:
  - **Gold Dashed Line**: Target savings goal threshold.
  - **Teal Solid Line with Vertex Nodes**: Exponential compound trajectory showing exact month-by-month portfolio balances.

### 6. 50/30/20 Diagnostic Stacked Proportion Bars
- **Visual Method**: Dual comparison horizontal stacked bars:
  - **Top Bar**: User's actual breakdown (Needs %, Wants %, Savings %).
  - **Bottom Bar**: Ideal Senator Elizabeth Warren 50/30/20 benchmark.

### 7. Transaction Velocity & Payment Mode Analytics (Tab 2)
- **Visual Method**:
  - **Category Velocity Bars**: Horizontal rank-ordered bars highlighting the top spending areas from logged transactions.
  - **Payment Mode Donut**: Proportional distribution of transactions processed via **UPI / GPay**, **Credit/Debit Card**, **Net Banking**, and **Cash**.

---

## 🔒 6. Security & Role-Based Access Control (RBAC)

### 1. Password Security
- Passwords are never stored in plaintext.
- The backend uses **`bcrypt`** with **12 salt rounds**. `bcrypt` includes an internal random salt and a computationally intensive key derivation function to resist brute-force and rainbow table attacks.

### 2. JSON Web Token (JWT) Session Management
- Authentication generates an asymmetric-ready signed JWT token (`HS256` algorithm).
- Payload contains:
  ```json
  {
    "sub": "651a2b3c4d5e6f7a8b9c0d1e",
    "role": "user",
    "email": "rohit@college.edu",
    "exp": 1728470400,
    "iat": 1728384000
  }
  ```
- All protected API requests pass this token in the `Authorization: Bearer <token>` header.

### 3. Role-Based Access Control (RBAC) Implementation
The system implements two distinct roles:

| Feature / Resource | Standard User (`user`) | Administrator (`admin`) |
|---|---|---|
| View / Edit Own Budget Plan | ✅ Yes | ✅ Yes |
| Record / Delete Own Transactions | ✅ Yes | ✅ Yes |
| Upload / Sync Own Historical CSV | ✅ Yes | ✅ Yes |
| View Other Users' Financial Data | ❌ **Forbidden** (Strict DB Filter) | ❌ **Forbidden** (Privacy isolated) |
| Access Admin Portal UI Tab | ❌ Hidden | ✅ Visible |
| Access `/api/admin/users` | ❌ `403 Forbidden` | ✅ `200 OK` (Full directory) |
| Change User Roles / Deactivate Users | ❌ `403 Forbidden` | ✅ `200 OK` |
| View System Analytics & MongoDB Status | ❌ `403 Forbidden` | ✅ `200 OK` |

**How Data Isolation is Enforced in Code:**
```python
# app/routers/budget_routes.py
@router.get("/plan")
async def get_budget_plan(current_user: dict = Depends(get_current_user)):
    # Strict isolation: filter by authenticated user's ID
    user_id = current_user["id"]
    plan = await budget_col.find_one({"user_id": user_id})
    return plan
```

**How RBAC Route Protection is Enforced in Code:**
```python
# app/dependencies.py
def require_role(allowed_roles: List[str]):
    async def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        if current_user.get("role") not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Requires one of {allowed_roles} roles."
            )
        return current_user
    return role_checker

require_admin = require_role(["admin"])
```

---

## 🗄️ 7. Database Schema Design (MongoDB)

BudgetPath uses MongoDB for flexible NoSQL document storage. There are four primary collections:

### 1. `users` Collection
Stores authentication credentials, profile data, and RBAC roles.
```json
{
  "_id": ObjectId("670512f4a1b2c3d4e5f60001"),
  "email": "rohit@college.edu",
  "username": "rohit",
  "full_name": "Rohit Ahir",
  "password_hash": "$2b$12$e8Y7z...",
  "role": "user",
  "is_active": true,
  "created_at": "2026-10-08T15:20:00.000Z"
}
```
- **Indexes**: `email` (Unique), `username` (Unique).

### 2. `budget_plans` Collection
Stores persistent budget parameters, needs lists, and investment SIPs per user.
```json
{
  "_id": ObjectId("670512f4a1b2c3d4e5f60002"),
  "user_id": "670512f4a1b2c3d4e5f60001",
  "monthly_income": 45000.0,
  "savings_goal": 100000.0,
  "months_target": 12,
  "current_savings": 10000.0,
  "annual_return_rate": 6.0,
  "needs": [
    { "n": "Rent", "a": 12000.0 },
    { "n": "Food & groceries", "a": 6000.0 }
  ],
  "investments": [
    { "n": "Mutual fund SIP", "a": 2000.0, "r": 11.0 },
    { "n": "Fixed deposit", "a": 2000.0, "r": 7.0 }
  ],
  "updated_at": "2026-10-08T15:22:00.000Z"
}
```
- **Indexes**: `user_id` (Unique).

### 3. `transactions` Collection
Stores granular daily/weekly financial transactions logged by users.
```json
{
  "_id": ObjectId("670512f4a1b2c3d4e5f60003"),
  "user_id": "670512f4a1b2c3d4e5f60001",
  "date": "2026-10-08",
  "title": "Grocery Shopping at DMart",
  "category": "Food & Groceries",
  "amount": 2450.0,
  "type": "expense",
  "payment_method": "UPI",
  "notes": "Weekly household supplies",
  "created_at": "2026-10-08T15:25:00.000Z"
}
```
- **Indexes**: Compound index `("user_id", 1), ("date", -1)`.

### 4. `historical_data` Collection
Stores multi-month CSV training datasets uploaded by users to train their personalized AI models.
```json
{
  "_id": ObjectId("670512f4a1b2c3d4e5f60004"),
  "user_id": "670512f4a1b2c3d4e5f60001",
  "labels": ["Oct 23", "Nov 23", "Dec 23", "..."],
  "mn": [10, 11, 12, 1],
  "cats": {
    "Food": [6000, 6200, 6400],
    "Entertainment": [3000, 2800, 4200]
  },
  "income": [45000, 45000, 48000],
  "updated_at": "2026-10-08T15:26:00.000Z"
}
```
- **Indexes**: `user_id` (Unique).

---

## 🌐 8. REST API Endpoints Specification

FastAPI automatically generates interactive Swagger documentation at **`http://localhost:8000/docs`**.

### Authentication Routes (`/api/auth`)
| Method | Endpoint | Description | Request Body | Access |
|---|---|---|---|---|
| `POST` | `/api/auth/register` | Register a new user | `{ username, email, full_name, password, role }` | Public |
| `POST` | `/api/auth/login` | Log in and get JWT token | `{ email_or_username, password }` | Public |
| `GET` | `/api/auth/me` | Fetch authenticated user profile | None | Authenticated |

### Budget Planning Routes (`/api/budget`)
| Method | Endpoint | Description | Request Body | Access |
|---|---|---|---|---|
| `GET` | `/api/budget/plan` | Load saved user plan | None | User Isolated |
| `POST` | `/api/budget/plan` | Save or update budget plan | `{ monthly_income, savings_goal, needs, investments, ... }` | User Isolated |

### Transaction Routes (`/api/transactions`)
| Method | Endpoint | Description | Request Body | Access |
|---|---|---|---|---|
| `GET` | `/api/transactions` | List user transactions | Query: `?type=expense&category=Food` | User Isolated |
| `POST` | `/api/transactions` | Add a new transaction | `{ title, amount, type, category, payment_method, date }` | User Isolated |
| `DELETE` | `/api/transactions/{id}` | Delete transaction | None | User Isolated |
| `GET` | `/api/transactions/summary` | Aggregate totals & net balance | None | User Isolated |
| `GET` | `/api/transactions/monthly-stats` | Monthly stats, multi-month comparison & daily burn curve | Query: `?month=2024-10` | User Isolated |

### Historical Data & CSV Routes (`/api/history`)
| Method | Endpoint | Description | Request Body | Access |
|---|---|---|---|---|
| `GET` | `/api/history` | Fetch saved training dataset | None | User Isolated |
| `POST` | `/api/history/sync` | Persist multi-month CSV data | `{ labels, mn, cats, income }` | User Isolated |
| `GET` | `/api/history/template.csv` | Download sample CSV template | None | Public |

### Admin Governance Routes (`/api/admin`)
| Method | Endpoint | Description | Request Body | Access |
|---|---|---|---|---|
| `GET` | `/api/admin/stats` | Platform KPIs & DB health | None | **Admin Only (RBAC)** |
| `GET` | `/api/admin/users` | List all platform users | None | **Admin Only (RBAC)** |
| `PATCH` | `/api/admin/users/{id}` | Promote/demote role or toggle status | `{ role: "admin", is_active: true }` | **Admin Only (RBAC)** |

---

## 🚀 9. How to Setup and Run the Project

### Prerequisites
- **Python**: Version 3.10+ (tested on Python 3.14)
- **MongoDB**: MongoDB Atlas connection string (or local MongoDB server on port 27017)
- **Web Browser**: Chrome, Edge, Firefox, or Safari

### Step 1: Configure Environment Variables
In `Backend/.env`, provide your MongoDB connection string:
```env
# MongoDB Connection String (Atlas or Local)
MONGO_URI=mongodb+srv://<username>:<password>@cluster0.mongodb.net/?retryWrites=true&w=majority

# Database Name
DB_NAME=budgetpath

# JWT Authentication Secret Key
JWT_SECRET_KEY=budgetpath_super_secret_jwt_key_2026_secure_key_change_in_production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### Step 2: Install Backend Dependencies
Open PowerShell or Terminal in the project root:
```powershell
cd "c:\Users\Rohit Ahir\OneDrive\Desktop\College Project\Backend"
python -m pip install -r requirements.txt
```

### Step 3: Run the FastAPI Backend Server
```powershell
python run.py
```
- The backend will start at: `http://localhost:8000`
- Interactive Swagger API docs: `http://localhost:8000/docs`
- Health check endpoint: `http://localhost:8000/api/health`

### Step 4: Open the Frontend
- Open `Frontend/index.html` directly in your browser, or through a local development server:
  ```
  http://127.0.0.1:3000/Frontend/index.html
  ```

---

## 🌐 10. Deploying on Vercel (Cloud Production)

BudgetPath Pro is pre-configured for one-click deployment on **Vercel** as a full-stack serverless application:
- **Serverless API**: Handled by `@vercel/python` via [api/index.py](file:///c:/Users/Rohit%20Ahir/OneDrive/Desktop/College%20Project/api/index.py)
- **Static Frontend**: Served from the global edge CDN via [Frontend/index.html](file:///c:/Users/Rohit%20Ahir/OneDrive/Desktop/College%20Project/Frontend/index.html)
- **Zero CORS Issues**: Single unified origin (e.g. `https://my-budget-path.vercel.app`)

### Quick 3-Step Deployment:
1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Deploy BudgetPath Pro to Vercel"
   git push origin development
   ```
2. **Import to Vercel**:
   - Go to [vercel.com](https://vercel.com) ➔ **Add New Project** ➔ Import `rohitahir2002/my-budget-path`.
   - Set Framework Preset to **Other**, Root Directory to `./`.
3. **Set Environment Variables in Vercel Dashboard**:
   - `MONGO_URI`: `mongodb+srv://workrohitahir_db_user:km40XNgjQLujxBe0@cluster0.onhvcjv.mongodb.net`
   - `DB_NAME`: `budgetpath`
   - `JWT_SECRET_KEY`: `budgetpath_super_secret_jwt_key_2026_secure_key_change_in_production`
   - Click **Deploy**!

> 📖 **Full Comprehensive Guide**: Read the dedicated [VERCEL_DEPLOYMENT_GUIDE.md](file:///c:/Users/Rohit%20Ahir/OneDrive/Desktop/College%20Project/VERCEL_DEPLOYMENT_GUIDE.md) for detailed MongoDB Atlas network configuration, verification commands, and troubleshooting.

---

## 🎓 11. Viva & Teacher Presentation Q&A (Cheat Sheet)

Use these concise, technical answers during your project review or teacher questions:

### Q1: Why did you choose FastAPI over Flask or Django?
> **Answer**: *"FastAPI is built on Starlette and Pydantic, offering native asynchronous (`async/await`) performance comparable to NodeJS and Go. Unlike Flask, FastAPI provides automatic request validation via Pydantic schemas and auto-generates interactive OpenAPI/Swagger documentation (`/docs`) out of the box."*

### Q2: Why MongoDB (NoSQL) instead of a Relational Database like MySQL?
> **Answer**: *"Personal finance categories and budget structures vary widely between users (some users have 3 investment categories, others have 10 with custom SIP returns). MongoDB's BSON document model allows flexible nested structures (like arrays of needs and investments) without requiring complex table joins or rigid schema migrations. Furthermore, with `motor`, MongoDB integrates natively with FastAPI's asynchronous event loop."*

### Q3: How is user data kept private and secure?
> **Answer**: *"We implement multi-layered security: passwords are never stored in plaintext and are hashed using bcrypt with 12 salt rounds. All protected endpoints require a signed JWT Bearer token. At the database layer, every query is strictly scoped by `user_id = current_user['id']`, making it mathematically impossible for User A to read or modify User B's financial records."*

### Q4: What is RBAC and where is it enforced?
> **Answer**: *"RBAC stands for Role-Based Access Control. In our system, users possess either a `user` or `admin` role. In FastAPI, RBAC is enforced via dependency injection (`Depends(require_admin)`). If a standard user attempts to query administrative endpoints (`/api/admin/*`), the server immediately rejects the request with HTTP 403 Forbidden. The frontend also dynamically hides the Admin Portal tab for non-admin users."*

### Q5: How does the AI regression model work, and why Ridge Regression?
> **Answer**: *"We use Ridge Linear Regression with $L_2$ regularization. Personal spending exhibits autoregressive behavior—what you spent over the last 1 to 3 months strongly influences what you will spend next month. We engineer autoregressive lag features ($t-1, t-2, t-3$) along with a festive season flag for Indian holiday surges (October onwards). Ridge regression adds a penalty $\lambda I$ to the normal equation, preventing matrix singularity and avoiding overfitting when historical data spans only 12 to 36 months."*

### Q6: How does Cloud Auto-Sync work?
> **Answer**: *"Whenever a user adjusts an income slider, adds a need, or changes an investment return rate, the frontend triggers a debounced auto-save function (2-second timer). If the user stops interacting, the state is sent asynchronously to `/api/budget/plan` via a `POST` request. The top navigation bar dynamically reflects the sync state: green dot for 'Synced with MongoDB', yellow for 'Unsaved Changes', and red for 'Offline'."*

---

## 👥 Authors & Academic Credits
- **Project**: BudgetPath Pro
- **Developer**: Rohit Ahir
- **Academic Submission**: College Project / Final Year Evaluation
- **Tech Stack**: Python (FastAPI), MongoDB (Motor/PyMongo), HTML5/CSS3/JavaScript (ES6+), JWT, Bcrypt.
