import logging
import certifi
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

logger = logging.getLogger("budgetpath.db")

client: AsyncIOMotorClient = None
db = None


def init_db():
    global client, db
    if db is None or client is None:
        client_kwargs = {
            "serverSelectionTimeoutMS": 5000
        }
        # If connecting to MongoDB Atlas (mongodb+srv), supply certifi CA bundle
        if "mongodb+srv://" in settings.MONGO_URI or "tls=true" in settings.MONGO_URI.lower():
            client_kwargs["tlsCAFile"] = certifi.where()

        client = AsyncIOMotorClient(
            settings.MONGO_URI,
            **client_kwargs
        )
        db = client[settings.DB_NAME]
    return db


async def connect_to_mongo():
    global client, db
    try:
        logger.info(f"Connecting to MongoDB at {settings.MONGO_URI}...")
        init_db()
        
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
    global db
    if db is None:
        init_db()
    return db


def get_users_collection():
    database = get_db()
    if database is not None:
        return database["users"]
    return None


def get_budget_collection():
    database = get_db()
    if database is not None:
        return database["budget_plans"]
    return None


def get_transactions_collection():
    database = get_db()
    if database is not None:
        return database["transactions"]
    return None


def get_history_collection():
    database = get_db()
    if database is not None:
        return database["historical_data"]
    return None
