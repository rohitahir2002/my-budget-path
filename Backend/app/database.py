import logging
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

logger = logging.getLogger("budgetpath.db")

client: AsyncIOMotorClient = None
db = None


async def connect_to_mongo():
    global client, db
    try:
        logger.info(f"Connecting to MongoDB at {settings.MONGO_URI}...")
        client = AsyncIOMotorClient(
            settings.MONGO_URI,
            serverSelectionTimeoutMS=5000
        )
        db = client[settings.DB_NAME]
        
        # Test connection ping
        await client.admin.command("ping")
        logger.info("Successfully connected to MongoDB!")

        # Create indexes
        users = db["users"]
        await users.create_index("email", unique=True)
        await users.create_index("username", unique=True)

        budget_plans = db["budget_plans"]
        await budget_plans.create_index("user_id", unique=True)

        transactions = db["transactions"]
        await transactions.create_index([("user_id", 1), ("date", -1)])

        history = db["historical_data"]
        await history.create_index("user_id", unique=True)

    except Exception as e:
        logger.warning(f"Could not connect to MongoDB at startup: {e}. Please ensure MongoDB is running or connection string in .env is correct.")


async def close_mongo_connection():
    global client
    if client:
        client.close()
        logger.info("Closed MongoDB connection.")


def get_db():
    return db


def get_users_collection():
    if db is not None:
        return db["users"]
    return None


def get_budget_collection():
    if db is not None:
        return db["budget_plans"]
    return None


def get_transactions_collection():
    if db is not None:
        return db["transactions"]
    return None


def get_history_collection():
    if db is not None:
        return db["historical_data"]
    return None
