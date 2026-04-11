from motor.motor_asyncio import AsyncIOMotorClient

mongo_url = "mongodb://Localhost:27017"

client = AsyncIOMotorClient(mongo_url)

db = client["fastapi_db"]
product_collection = db ["products"]
user_collection = db["users"]
