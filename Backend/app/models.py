from typing import Optional, List, Dict
from pydantic import BaseModel, Field


# ------------------ User Models ------------------
class UserRegister(BaseModel):
    email: str
    username: str
    password: str
    full_name: Optional[str] = None
    role: str = Field(default="user", description="user or admin")


class UserLogin(BaseModel):
    email_or_username: str
    password: str


class UserOut(BaseModel):
    id: str
    email: str
    username: str
    full_name: Optional[str] = None
    role: str
    created_at: str
    is_active: bool = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ------------------ Budget Plan Models ------------------
class NeedItem(BaseModel):
    n: str = Field(..., alias="name", description="Category/Name of the need")
    a: float = Field(..., alias="amount", description="Monthly amount in ₹")

    class Config:
        populate_by_name = True


class InvestmentItem(BaseModel):
    n: str = Field(..., alias="name", description="Name of the investment")
    a: float = Field(..., alias="amount", description="Monthly amount in ₹")
    r: float = Field(default=8.0, alias="return_rate", description="Annual return %")

    class Config:
        populate_by_name = True


class BudgetPlanData(BaseModel):
    monthly_income: float = 45000.0
    savings_goal: float = 100000.0
    months_target: int = 12
    current_savings: float = 10000.0
    annual_return_rate: float = 6.0
    needs: List[NeedItem] = []
    investments: List[InvestmentItem] = []


class BudgetPlanOut(BudgetPlanData):
    user_id: str
    updated_at: str


# ------------------ Transaction Models ------------------
class TransactionCreate(BaseModel):
    date: str
    title: str
    category: str
    amount: float
    type: str = Field(default="expense", description="'expense' or 'income'")
    payment_method: str = "UPI"
    notes: Optional[str] = ""


class TransactionOut(BaseModel):
    id: str
    user_id: str
    date: str
    title: str
    category: str
    amount: float
    type: str
    payment_method: str
    notes: Optional[str] = ""
    created_at: str


# ------------------ History / Cloud CSV Models ------------------
class HistoricalDataPayload(BaseModel):
    labels: List[str]
    mn: List[int]
    cats: Dict[str, List[float]]
    income: List[float]


# ------------------ Admin Models ------------------
class AdminUserUpdate(BaseModel):
    role: Optional[str] = None
    is_active: Optional[bool] = None


class SystemStats(BaseModel):
    total_users: int
    active_users: int
    admin_users: int
    total_transactions: int
    total_budget_plans: int
    mongodb_status: str
