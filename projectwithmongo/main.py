from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.security import OAuth2PasswordBearer
from bson import ObjectId
from bson.errors import InvalidId
from jose import JWTError, jwt

from mongodb import product_collection, user_collection
from models import Product, User, LoginUser
from auth import hash_password, verify_password, create_access_token


app = FastAPI()


# ---------------- CONFIG ----------------

SECRET_KEY = ""
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# ---------------- UTILITIES ----------------

def product_helper(product) -> dict:
    return {
        "id": str(product["_id"]),
        "name": product.get("name"),
        "description": product.get("description"),
        "price": product.get("price"),
        "quantity": product.get("quantity"),
    }


def to_object_id(product_id: str):
    try:
        return ObjectId(product_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid product ID")


# ---------------- AUTH ----------------

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")

        if not email:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        user = await user_collection.find_one({"email": email})

        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return user

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


# ---------------- AUTH ROUTES ----------------

@app.post("/register")
async def register(user: User):
    # check existing user
    existing_user = await user_collection.find_one({"email": user.email})

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")

    # safety check (prevents bcrypt crash issue indirectly)
    if len(user.password.encode("utf-8")) > 72:
        raise HTTPException(
            status_code=400,
            detail="Password too long (bcrypt limit is 72 bytes)"
        )

    hashed_password = hash_password(user.password)

    await user_collection.insert_one({
        "email": user.email,
        "password": hashed_password
    })

    return {"message": "User registered successfully"}


@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # We use form_data.username because Swagger sends the email in that field
    db_user = await user_collection.find_one({"email": form_data.username})

    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not verify_password(form_data.password, db_user["password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # Create the token using the email found in the database
    token = create_access_token({"sub": db_user["email"]})

    return {
        "access_token": token, 
        "token_type": "bearer"
    }


@app.get("/profile")
async def profile(current_user=Depends(get_current_user)):
    return {
        "email": current_user.get("email")
    }


# ---------------- PRODUCT CRUD ----------------

@app.post("/products/")
async def create_product(
    product: Product,
    current_user=Depends(get_current_user)
):
    data = product.model_dump(by_alias=True, exclude={"id"})

    result = await product_collection.insert_one(data)

    return {
        "message": "Product created",
        "id": str(result.inserted_id)
    }


@app.get("/products/")
async def get_products(current_user=Depends(get_current_user)):
    products = []

    async for p in product_collection.find():
        products.append(product_helper(p))

    return products


@app.get("/products/{product_id}")
async def get_product(
    product_id: str,
    current_user=Depends(get_current_user)
):
    _id = to_object_id(product_id)

    product = await product_collection.find_one({"_id": _id})

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product_helper(product)


@app.put("/products/{product_id}")
async def update_product(
    product_id: str,
    product: Product,
    current_user=Depends(get_current_user)
):
    _id = to_object_id(product_id)

    update_data = product.model_dump(by_alias=True, exclude={"id"})

    result = await product_collection.update_one(
        {"_id": _id},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")

    return {"message": "Product updated successfully"}


@app.delete("/products/{product_id}")
async def delete_product(
    product_id: str,
    current_user=Depends(get_current_user)
):
    _id = to_object_id(product_id)

    result = await product_collection.delete_one({"_id": _id})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")

    return {"message": "Product deleted successfully"}