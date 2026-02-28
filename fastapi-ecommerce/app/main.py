from datetime import datetime
from uuid import uuid4
from uuid import UUID
from fastapi import FastAPI, HTTPException, Query, Path
from service.products import get_all_products, add_product, remove_product, update_product
from schema.product import Product

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Welcome to FastAPI"}

# #Dynamic routing
# @app.get("/products")
# def get_products():
#     return get_all_products()

@app.get("/products")
def list_products(
    name: str = Query(
        default=None,
        min_length=1,
        max_length=50,
        description="Search by name (Case insensitive)"
    ),
    sorted_by_price: bool = Query(default=False, description="Sorted by price"),
    order: str = Query(
        default="asc", description="Sort when sorted_by_price=true (asc,desc)"
    )
):
    products = get_all_products()

    if name:
        needle = name.strip().lower()
        products = [p for p in products if needle in p.get("name", "").lower()]

    if not products:
        raise HTTPException(
            status_code=404, detail=f"No product found matching name={name}"

        )
    
    if sorted_by_price:
        reverse = order == "desc"
        products = sorted(products, key=lambda p: p.get("price", 0), reverse=reverse)

    return {"total": len(products), "items": products}
    
@app.get("/products/{product_id}")
def get_product_id(
    product_id: str = Path(
    ..., min_length=36, 
    max_length=36, 
    description= "ID of the products",
    example="0005a4ea-ce3f-4dd7-bee0-f4ccc70fea6a"
    )
):
    products=get_all_products()
    for product in products:
        if product["id"]== product_id:
            return product
        raise HTTPException(status_code=404, detail="Page not found!")
    
@app.post("/products", status_code=201)
def create_product(product: Product):
    product_dict = product.model_dump(mode="json")
    product_dict["id"] = str(uuid4())
    product_dict["created_at"] = datetime.utcnow().isoformat() + "Z"

    try:
        add_product(product_dict)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return product.model_dump(mode="json")

@app.delete("/products/{product_id}")
def delete_product(
    product_id: UUID = Path(
        ...,
        description="Product UUID",
        example="6c7b7c69-f07f-4474-992e-58d3c48ac437"
    )
):
    try:
        res = remove_product(str(product_id))
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.put("/products/{product_id}")
def update_product_endpoint(
    product_id: UUID = Path(
        ...,
        description="Product UUID",
        example="6c7b7c69-f07f-4474-992e-58d3c48ac437"
    ),
    product: Product = ...
):
    try:
        updated = update_product(str(product_id), product.model_dump(mode="json"))
        return updated
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))